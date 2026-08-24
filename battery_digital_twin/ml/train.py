"""
Training pipeline for the Battery Digital Twin ML layer.

1. Feature engineering: rolling 7/30-day averages, cumulative cycle count,
   temperature exposure index, fast-charge ratio.
2. Trains an XGBoost regressor to predict Remaining Useful Life (RUL, in days).
3. Trains an XGBoost classifier to predict 90-day failure probability.
4. Combines both into a Battery Health Index (0-100) - formula documented below.
5. Saves both trained models to model_rul.json and model_failure.json.

Run from the ml/ directory: python3 train.py
Expects ../data/battery_telemetry.csv to already exist (run data/generate_data.py first).
"""

import numpy as np
import pandas as pd
from xgboost import XGBRegressor, XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, roc_auc_score

FAILURE_CAPACITY_THRESHOLD = 70.0  # must match data/generate_data.py
FAILURE_WINDOW_DAYS = 90           # "90-day failure probability" horizon

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


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds rolling averages, cumulative cycle count, temperature exposure index,
    and fast-charge ratio, computed per-battery over time.
    """
    df = df.sort_values(["battery_id", "day"]).copy()
    g = df.groupby("battery_id")

    df["capacity_roll7"] = g["capacity_pct"].transform(lambda s: s.rolling(7, min_periods=1).mean())
    df["capacity_roll30"] = g["capacity_pct"].transform(lambda s: s.rolling(30, min_periods=1).mean())
    df["temp_roll7"] = g["temperature"].transform(lambda s: s.rolling(7, min_periods=1).mean())
    df["temp_roll30"] = g["temperature"].transform(lambda s: s.rolling(30, min_periods=1).mean())

    # Cumulative cycle count is just cycle_count itself (already cumulative in
    # the raw data), kept as an explicit named feature for clarity/contract.
    df["cum_cycle_count"] = df["cycle_count"]

    # Temperature exposure index: rolling-30 mean temp scaled against a 25C
    # baseline, roughly capturing cumulative thermal stress.
    df["temp_exposure_index"] = (df["temp_roll30"] - 25.0).clip(lower=0)

    # Fast-charge ratio over the trailing 30 days.
    df["fast_charge_ratio_30"] = g["fast_charge_freq"].transform(
        lambda s: s.rolling(30, min_periods=1).mean()
    )

    return df


MAX_RUL_CAP_DAYS = 1500  # cap so a near-flat degradation slope doesn't blow up


def add_labels(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds supervised-learning targets per battery:
      - rul_days: days remaining until capacity_pct is projected to cross
        FAILURE_CAPACITY_THRESHOLD. If the battery actually crosses the
        threshold within the observed 365-day window, we use the real
        crossing day. If it never crosses within the window (a healthy
        battery), we fit a linear trend to its observed capacity decay and
        extrapolate forward to estimate when it WOULD cross - otherwise
        every healthy battery would get an artificially tiny RUL simply
        because the simulation window ends at day 365.
      - failure_within_90d: 1 if the (real or projected) crossing day is
        within FAILURE_WINDOW_DAYS of the current row, else 0.
    """
    out = []
    for battery_id, grp in df.groupby("battery_id"):
        grp = grp.sort_values("day").reset_index(drop=True)
        below = grp["capacity_pct"] < FAILURE_CAPACITY_THRESHOLD

        if below.any():
            failure_day = grp.loc[below, "day"].iloc[0]
        else:
            # Fit a linear trend (capacity_pct ~ day) and project forward to
            # the day it would cross the failure threshold.
            slope, intercept = np.polyfit(grp["day"], grp["capacity_pct"], 1)
            if slope < -1e-6:
                projected_day = (FAILURE_CAPACITY_THRESHOLD - intercept) / slope
                failure_day = min(projected_day, grp["day"].max() + MAX_RUL_CAP_DAYS)
            else:
                # Flat or improving trend - treat as "very long" runway.
                failure_day = grp["day"].max() + MAX_RUL_CAP_DAYS

        grp["rul_days"] = (failure_day - grp["day"]).clip(lower=0, upper=MAX_RUL_CAP_DAYS)
        grp["failure_within_90d"] = (
            (failure_day - grp["day"]) <= FAILURE_WINDOW_DAYS
        ).astype(int)
        out.append(grp)
    return pd.concat(out, ignore_index=True)


def compute_bhi(rul_days: np.ndarray, failure_risk_pct: np.ndarray, capacity_pct: np.ndarray) -> np.ndarray:
    """
    Battery Health Index (0-100).

    BHI = 0.45 * capacity_score + 0.35 * rul_score + 0.20 * (100 - failure_risk_pct)

    Where:
      - capacity_score = capacity_pct directly (already 0-100).
      - rul_score = min(rul_days, 365) / 365 * 100 (caps benefit of very long RUL).
      - failure_risk_pct = predicted 90-day failure probability * 100.

    Weights: capacity is the most direct signal of current health (45%), RUL
    captures forward-looking runway (35%), and failure risk captures near-term
    volatility the other two terms might miss (20%). Documented here so the
    number is defensible in a demo/judging context.
    """
    capacity_score = np.clip(capacity_pct, 0, 100)
    rul_score = np.clip(rul_days, 0, 365) / 365.0 * 100.0
    risk_score = 100.0 - np.clip(failure_risk_pct, 0, 100)
    bhi = 0.45 * capacity_score + 0.35 * rul_score + 0.20 * risk_score
    return np.clip(bhi, 0, 100)


def main():
    raw = pd.read_csv("../data/battery_telemetry.csv")
    df = engineer_features(raw)
    df = add_labels(df)
    df = df.dropna(subset=FEATURE_COLUMNS + ["rul_days", "failure_within_90d"])

    X = df[FEATURE_COLUMNS]
    y_rul = df["rul_days"]
    y_fail = df["failure_within_90d"]

    X_train, X_test, y_rul_train, y_rul_test, y_fail_train, y_fail_test = train_test_split(
        X, y_rul, y_fail, test_size=0.2, random_state=42
    )

    # --- RUL regressor ------------------------------------------------
    rul_model = XGBRegressor(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.08,
        subsample=0.9,
        colsample_bytree=0.9,
        random_state=42,
    )
    rul_model.fit(X_train, y_rul_train)
    rul_pred = rul_model.predict(X_test)
    rul_mae = mean_absolute_error(y_rul_test, rul_pred)
    print(f"RUL regressor - MAE: {rul_mae:.1f} days")

    # --- Failure classifier --------------------------------------------
    fail_model = XGBClassifier(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.08,
        subsample=0.9,
        colsample_bytree=0.9,
        random_state=42,
        eval_metric="logloss",
    )
    fail_model.fit(X_train, y_fail_train)
    fail_pred_proba = fail_model.predict_proba(X_test)[:, 1]
    if y_fail_test.nunique() > 1:
        fail_auc = roc_auc_score(y_fail_test, fail_pred_proba)
        print(f"Failure classifier - ROC-AUC: {fail_auc:.3f}")
    else:
        print("Failure classifier - only one class present in test split, skipping AUC")

    rul_model.save_model("model_rul.json")
    fail_model.save_model("model_failure.json")
    print("Saved model_rul.json and model_failure.json")

    # Quick end-to-end sanity check on a few batteries using the latest row
    # per battery (mirrors what predict.py will do at inference time).
    latest = df.sort_values("day").groupby("battery_id").tail(1)
    latest_X = latest[FEATURE_COLUMNS]
    latest_rul_pred = rul_model.predict(latest_X)
    latest_fail_pred = fail_model.predict_proba(latest_X)[:, 1] * 100
    latest_bhi = compute_bhi(latest_rul_pred, latest_fail_pred, latest["capacity_pct"].values)

    summary = pd.DataFrame(
        {
            "battery_id": latest["battery_id"].values,
            "capacity_pct": latest["capacity_pct"].values,
            "predicted_rul_days": latest_rul_pred.round(0),
            "predicted_failure_risk_pct": latest_fail_pred.round(1),
            "bhi": latest_bhi.round(1),
        }
    ).sort_values("bhi")
    print("\nLatest-day predictions per battery (sanity check):")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
