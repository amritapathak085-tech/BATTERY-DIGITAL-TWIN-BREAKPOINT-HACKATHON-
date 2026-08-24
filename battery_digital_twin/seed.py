import csv
import os
from pathlib import Path
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent


def require(name: str):
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing {name}. Copy .env.example to .env and fill it in.")
    return value


def read_csv(name: str):
    with open(ROOT / "data" / name, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def clean_metadata(rows):
    return [
        {"id": r["id"], "vehicle_type": r["vehicle_type"], "install_date": r["install_date"]}
        for r in rows
    ]


def clean_telemetry(rows):
    return [
        {
            "battery_id": r["battery_id"],
            "day": r["day"],
            "voltage": float(r["voltage"]),
            "temperature": float(r["temperature"]),
            "cycle_count": int(r["cycle_count"]),
            "depth_of_discharge": float(r["depth_of_discharge"]),
            "fast_charge_freq": float(r["fast_charge_freq"]),
            "capacity_pct": float(r["capacity_pct"]),
        }
        for r in rows
    ]


def chunks(rows, size=500):
    for i in range(0, len(rows), size):
        yield rows[i:i + size]


def main():
    client = create_client(require("SUPABASE_URL"), require("SUPABASE_KEY"))
    metadata = clean_metadata(read_csv("battery_metadata.csv"))
    telemetry = clean_telemetry(read_csv("battery_telemetry.csv"))

    for batch in chunks(metadata):
        client.table("batteries").upsert(batch).execute()
    for batch in chunks(telemetry):
        client.table("telemetry").upsert(batch).execute()

    print(f"Seeded {len(metadata)} batteries and {len(telemetry)} telemetry rows.")


if __name__ == "__main__":
    main()
