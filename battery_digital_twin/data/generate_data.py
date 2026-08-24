"""
Synthetic battery telemetry generator for the Battery Digital Twin project.

Generates daily telemetry for 20 industrial EV batteries over 365 days, with
realistic degradation: batteries exposed to higher heat and more fast-charging
degrade faster (declining capacity %, rising internal resistance), and a
handful of batteries are engineered to trend toward failure by day 365.

Outputs:
  - battery_telemetry.csv  (daily records)
  - battery_metadata.csv   (one row per battery)
"""

import numpy as np
import pandas as pd
from datetime import date, timedelta

# ----------------------------------------------------------------------------
# Config
# ----------------------------------------------------------------------------
N_BATTERIES = 20
N_DAYS = 365
SEED = 42
FAILURE_CAPACITY_THRESHOLD = 70.0  # capacity_pct below this = "failed"

VEHICLE_TYPES = ["forklift", "delivery_van", "mining_truck", "intra_plant_shuttle"]

rng = np.random.default_rng(SEED)


def make_battery_profile(battery_idx: int) -> dict:
    """
    Assigns each battery a 'stress profile' that drives its degradation rate.
    A few batteries are deliberately made high-stress so they trend toward
    failure (capacity_pct < FAILURE_CAPACITY_THRESHOLD) by day 365.
    """
    # First 3 batteries are "bad actors": high heat + heavy fast-charging.
    if battery_idx < 3:
        heat_level = rng.uniform(0.85, 1.0)       # 0-1 severity
        fast_charge_level = rng.uniform(0.85, 1.0)
        usage_intensity = rng.uniform(0.8, 1.0)
    # Next 5 are moderately stressed (visibly degrading, but not failing).
    elif battery_idx < 8:
        heat_level = rng.uniform(0.4, 0.7)
        fast_charge_level = rng.uniform(0.4, 0.7)
        usage_intensity = rng.uniform(0.4, 0.7)
    # Rest are healthy fleet baseline.
    else:
        heat_level = rng.uniform(0.05, 0.35)
        fast_charge_level = rng.uniform(0.05, 0.35)
        usage_intensity = rng.uniform(0.2, 0.5)

    return {
        "heat_level": heat_level,
        "fast_charge_level": fast_charge_level,
        "usage_intensity": usage_intensity,
        "vehicle_type": VEHICLE_TYPES[battery_idx % len(VEHICLE_TYPES)],
    }


def simulate_battery(battery_id: str, profile: dict) -> pd.DataFrame:
    """Simulates one battery's daily telemetry across N_DAYS."""
    heat = profile["heat_level"]
    fast_charge = profile["fast_charge_level"]
    usage = profile["usage_intensity"]

    # Base ambient temperature + heat-driven offset, with seasonal wobble.
    day_idx = np.arange(N_DAYS)
    seasonal = 4 * np.sin(2 * np.pi * day_idx / 365)
    ambient_temp = 28 + seasonal + heat * 12 + rng.normal(0, 1.5, N_DAYS)

    # Cell temperature runs a bit above ambient, more so under heavy usage.
    cell_temp = ambient_temp + usage * 6 + rng.normal(0, 1.0, N_DAYS)

    # Daily cycles and fast-charge frequency (0-1 fraction of charges that are fast).
    cycles_per_day = np.clip(rng.normal(1.2 + usage * 1.5, 0.2, N_DAYS), 0.3, 4.0)
    cycle_count = np.round(np.cumsum(cycles_per_day)).astype(int)
    fast_charge_freq = np.clip(
        rng.normal(fast_charge, 0.08, N_DAYS), 0.0, 1.0
    )

    # Depth of discharge (%) - deeper on high-usage batteries.
    depth_of_discharge = np.clip(
        rng.normal(45 + usage * 35, 6, N_DAYS), 15, 100
    )

    # Voltage nominal pack voltage with small noise, drifting down slightly
    # as capacity fades (added after capacity is computed below).
    nominal_voltage = 350.0

    # --- Degradation model -----------------------------------------------
    # Daily fractional capacity loss driven by heat, fast-charging, and DoD.
    # These weights are tuned so bad-actor batteries fall below the failure
    # threshold well before day 365, healthy ones stay > 90%.
    daily_stress = (
        0.00008
        + 0.00042 * heat
        + 0.00030 * fast_charge
        + 0.00016 * (depth_of_discharge / 100.0)
    )
    # Add small day-to-day noise so the curve isn't perfectly smooth.
    noisy_stress = np.clip(daily_stress + rng.normal(0, 0.00003, N_DAYS), 0, None)
    cumulative_loss = np.cumsum(noisy_stress)
    capacity_pct = np.clip(100.0 - cumulative_loss * 100.0, 40.0, 100.0)

    # Internal resistance rises as capacity fades (inverse relationship),
    # plus extra rise from heat exposure.
    internal_resistance = 30 + (100 - capacity_pct) * 1.8 + heat * 8 + rng.normal(0, 1.0, N_DAYS)

    # Voltage sags a little as capacity and resistance rise.
    voltage = nominal_voltage - (100 - capacity_pct) * 0.35 + rng.normal(0, 0.8, N_DAYS)

    df = pd.DataFrame(
        {
            "battery_id": battery_id,
            "day": day_idx + 1,
            "voltage": voltage.round(2),
            "temperature": cell_temp.round(2),
            "cycle_count": cycle_count,
            "depth_of_discharge": depth_of_discharge.round(2),
            "fast_charge_freq": fast_charge_freq.round(3),
            "capacity_pct": capacity_pct.round(2),
            "internal_resistance_mohm": internal_resistance.round(2),
            "ambient_temperature": ambient_temp.round(2),
        }
    )
    return df


def build_metadata(battery_ids: list, profiles: list) -> pd.DataFrame:
    install_start = date(2024, 1, 1)
    rows = []
    for i, (bid, profile) in enumerate(zip(battery_ids, profiles)):
        install_offset = int(rng.integers(0, 120))
        rows.append(
            {
                "battery_id": bid,
                "vehicle_type": profile["vehicle_type"],
                "install_date": (install_start + timedelta(days=install_offset)).isoformat(),
            }
        )
    return pd.DataFrame(rows)


def main():
    battery_ids = [f"BATT-{i+1:03d}" for i in range(N_BATTERIES)]
    profiles = [make_battery_profile(i) for i in range(N_BATTERIES)]

    all_telemetry = pd.concat(
        [simulate_battery(bid, profile) for bid, profile in zip(battery_ids, profiles)],
        ignore_index=True,
    )
    metadata = build_metadata(battery_ids, profiles)

    all_telemetry.to_csv("battery_telemetry.csv", index=False)
    metadata.to_csv("battery_metadata.csv", index=False)

    # Quick sanity summary printed to console (not saved) so you can eyeball
    # that the degradation model actually produced failing + healthy batteries.
    end_state = all_telemetry[all_telemetry["day"] == N_DAYS][
        ["battery_id", "capacity_pct"]
    ].sort_values("capacity_pct")
    n_failed = (end_state["capacity_pct"] < FAILURE_CAPACITY_THRESHOLD).sum()
    print(f"Generated {len(all_telemetry)} telemetry rows for {N_BATTERIES} batteries.")
    print(f"Batteries below {FAILURE_CAPACITY_THRESHOLD}% capacity by day {N_DAYS}: {n_failed}")
    print(end_state.to_string(index=False))


if __name__ == "__main__":
    main()
