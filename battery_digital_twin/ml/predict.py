"""
Inference module for the Battery Digital Twin ML layer.

This is the file Aadya's FastAPI /predict endpoint calls, and the file
Amrita's explain.py/simulate.py build on top of (same feature contract).

Usage:
    from predict import predict

    result = predict("BATT-003")
    # -> {"bhi": 30.6, "rul_days": 3, "failure_risk_pct": 99.9}

    # Or pass a feature dict directly (used by simulate.py for what-if runs,
    # so it can rerun inference on MODIFIED inputs without touching the CSV):
    result = predict({
        "voltage": 330.0, "temperature": 35.0, "cycle_count": 400,
        "depth_of_discharge": 55.0, "fast_charge_freq": 0.3,
        "internal_resistance_mohm": 90.0, "ambient_temperature": 30.0,
        "capacity_roll7": 80.0, "capacity_roll30": 81.0,
        "temp_roll7": 34.0, "temp_roll30": 33.0, "cum_cycle_count": 400,
        "temp_exposure_index": 8.0, "fast_charge_ratio_30": 0.3,
    })
"""

import os
from typing import Union

import numpy as np
import pandas as pd
from xgboost import XGBRegressor, XGBClassifier

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_TELEMETRY_PATH = os.path.join(_THIS_DIR, "..", "data", "battery_telemetry.csv")
_MODEL_RUL_PATH = os.path.join(_THIS_DIR, "model_rul.json")
_MODEL_FAILURE_PATH = os.path.join(_THIS_DIR, "model_failure.json")

FEATURE_COLUMNS = [
    "voltage",
    "temperature",
    "cycle_count",
    "depth_of_discharge",
    "fast_charge_freq",
    "internal_resistance_mohm",
    "ambient_temperature",
    "capacity_roll7",
    "capacity_roll30",
    "temp_roll7",
    "temp_roll30",
    "cum_cycle_count",
    "temp_exposure_index",
    "fast_charge_ratio_30",
]

_rul_model = None
_fail_model = None
_telemetry_cache = None


def _load_models():
    global _rul_model, _fail_model
    if _rul_model is None:
        _rul_model = XGBRegressor()
        _rul_model.load_model(_MODEL_RUL_PATH)
    if _fail_model is None:
        _fail_model = XGBClassifier()
        _fail_model.load_model(_MODEL_FAILURE_PATH)
    return _rul_model, _fail_model


def _load_telemetry() -> pd.DataFrame:
    global _telemetry_cache
    if _telemetry_cache is None:
        # Import here (not at module top) to avoid a hard circular import
        # with train.py, and to keep this module import-light for the API.
        from train import engineer_features

        raw = pd.read_csv(_TELEMETRY_PATH)
        _telemetry_cache = engineer_features(raw)
    return _telemetry_cache


def _compute_bhi(rul_days: float, failure_risk_pct: float, capacity_pct: float) -> float:
    """Same formula as train.py's compute_bhi - kept in sync manually since
    this module avoids importing train.py's heavier training-time deps at
    prediction time. See train.py::compute_bhi for the documented rationale."""
    capacity_score = float(np.clip(capacity_pct, 0, 100))
    rul_score = float(np.clip(rul_days, 0, 365)) / 365.0 * 100.0
    risk_score = 100.0 - float(np.clip(failure_risk_pct, 0, 100))
    bhi = 0.45 * capacity_score + 0.35 * rul_score + 0.20 * risk_score
    return round(float(np.clip(bhi, 0, 100)), 1)


def predict(battery_id_or_features: Union[str, dict]) -> dict:
    """
    Accepts EITHER:
      - a battery_id string (e.g. "BATT-003") -> looks up its latest known
        telemetry row and engineered features, or
      - a dict of already-engineered feature values (used by simulate.py for
        what-if runs on modified inputs).

    Returns: {"bhi": float, "rul_days": int, "failure_risk_pct": float}
    """
    rul_model, fail_model = _load_models()

    if isinstance(battery_id_or_features, str):
        telemetry = _load_telemetry()
        rows = telemetry[telemetry["battery_id"] == battery_id_or_features]
        if rows.empty:
            raise ValueError(f"Unknown battery_id: {battery_id_or_features}")
        latest_row = rows.sort_values("day").iloc[[-1]]
        X = latest_row[FEATURE_COLUMNS]
        capacity_pct = float(latest_row["capacity_pct"].iloc[0])
    elif isinstance(battery_id_or_features, dict):
        missing = set(FEATURE_COLUMNS) - set(battery_id_or_features.keys())
        if missing:
            raise ValueError(f"Missing required feature(s): {sorted(missing)}")
        X = pd.DataFrame([battery_id_or_features])[FEATURE_COLUMNS]
        # capacity_roll7 is the best available proxy for "current capacity"
        # when working from a raw feature dict rather than a stored row.
        capacity_pct = float(battery_id_or_features["capacity_roll7"])
    else:
        raise TypeError("battery_id_or_features must be a str battery_id or a feature dict")

    rul_days = float(rul_model.predict(X)[0])
    failure_risk_pct = float(fail_model.predict_proba(X)[:, 1][0]) * 100.0
    bhi = _compute_bhi(rul_days, failure_risk_pct, capacity_pct)

    return {
        "bhi": bhi,
        "rul_days": int(round(rul_days)),
        "failure_risk_pct": round(failure_risk_pct, 1),
    }


if __name__ == "__main__":
    # Quick manual smoke test - run `python3 predict.py` from the ml/ folder.
    for bid in ["BATT-001", "BATT-010", "BATT-006"]:
        print(bid, predict(bid))
