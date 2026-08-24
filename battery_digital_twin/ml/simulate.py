from typing import Any, Callable


# ---------------------------------------------------------
# DEMO / BUSINESS ASSUMPTIONS
# ---------------------------------------------------------

FAST_CHARGE_REDUCTION = 0.30

# These are named constants so they can be changed later
# without modifying the simulation logic.
BATTERY_REPLACEMENT_COST_INR = 150000
COST_PER_DOWNTIME_DAY_INR = 5000
CO2_PER_REPLACEMENT_KG = 500


def _default_predict(features: dict[str, Any]) -> dict[str, float]:
    """
    Temporary prediction function for development/testing.

    This is NOT the final ML model.
    It allows simulate.py to be tested before Kavya's
    predict.py is connected.
    """

    fast_charge = float(features.get("fast_charge_freq", 0))
    temperature = float(features.get("temperature", 35))
    cycle_count = float(features.get("cycle_count", 500))
    capacity = float(features.get("capacity_pct", 85))

    # Simple demo formulas.
    # These will eventually be replaced by the real ML model.
    bhi = (
        capacity
        - max(0, temperature - 35) * 0.4
        - fast_charge * 0.5
        - max(0, cycle_count - 500) * 0.01
    )

    bhi = max(0, min(100, bhi))

    rul_days = max(
        0,
        int(bhi * 3.0)
    )

    failure_risk = max(
        0,
        min(100, 100 - bhi)
    )

    return {
        "bhi": round(bhi, 2),
        "rul_days": rul_days,
        "failure_risk_pct": round(failure_risk, 2),
    }


def _calculate_savings(
    before: dict[str, float],
    after: dict[str, float]
) -> dict[str, float]:

    downtime_days_avoided = max(
        0,
        after["rul_days"] - before["rul_days"]
    )

    # Estimate economic benefit from additional usable days.
    downtime_savings = (
        downtime_days_avoided * COST_PER_DOWNTIME_DAY_INR
    )

    # Estimate avoided replacement cost if the scenario
    # meaningfully extends battery life.
    replacement_savings = (
        BATTERY_REPLACEMENT_COST_INR
        if after["rul_days"] > before["rul_days"] * 1.25
        else 0
    )

    co2_avoided = (
        CO2_PER_REPLACEMENT_KG
        if replacement_savings > 0
        else 0
    )

    return {
        "inr": round(
            downtime_savings + replacement_savings,
            2
        ),
        "downtime_days_avoided": downtime_days_avoided,
        "co2_kg": co2_avoided,
    }


def simulate_what_if(
    features: dict[str, Any],
    fast_charge_reduction: float = FAST_CHARGE_REDUCTION,
    predict_fn: Callable[
        [dict[str, Any]],
        dict[str, float]
    ] = _default_predict,
) -> dict[str, Any]:
    """
    Simulate reducing fast-charging frequency.

    Parameters
    ----------
    features:
        Current battery feature values.

    fast_charge_reduction:
        Fraction by which fast charging should be reduced.
        Example: 0.30 = 30% reduction.

    predict_fn:
        Prediction function.
        Eventually this will be Kavya's real ML prediction function.

    Returns
    -------
    dict:
        Before/after prediction and estimated savings.
    """

    if not 0 <= fast_charge_reduction <= 1:
        raise ValueError(
            "fast_charge_reduction must be between 0 and 1"
        )

    # -----------------------------------------------------
    # BEFORE
    # -----------------------------------------------------

    before = predict_fn(features)

    # -----------------------------------------------------
    # AFTER
    # -----------------------------------------------------

    modified_features = features.copy()

    original_fast_charge = float(
        modified_features.get("fast_charge_freq", 0)
    )

    modified_features["fast_charge_freq"] = (
        original_fast_charge
        * (1 - fast_charge_reduction)
    )

    after = predict_fn(modified_features)

    # -----------------------------------------------------
    # SAVINGS
    # -----------------------------------------------------

    savings = _calculate_savings(
        before,
        after
    )

    return {
        "scenario": {
            "parameter": "fast_charge_freq",
            "reduction_pct": round(
                fast_charge_reduction * 100,
                1
            ),
            "original_value": original_fast_charge,
            "new_value": round(
                modified_features["fast_charge_freq"],
                2
            ),
        },
        "before": before,
        "after": after,
        "savings": savings,
    }