"use client";

import Link from "next/link";
import { Battery } from "@/lib/types";
import RiskBadge from "./RiskBadge";

interface Props {
  battery: Battery;
}

export default function BatteryCard({ battery }: Props) {
  const healthClass =
    battery.bhi >= 70
      ? "health-good"
      : battery.bhi >= 45
      ? "health-medium"
      : "health-danger";

  return (
    <Link
      href={`/batteries/${battery.id}`}
      className="battery-card"
    >
      <div className="card-top">
        <div>
          <p className="battery-id">{battery.id}</p>
          <h3>{battery.name}</h3>
        </div>

        <RiskBadge risk={battery.risk_pct} />
      </div>

      <p className="vehicle-type">{battery.vehicle_type}</p>

      <div className="health-row">
        <div>
          <span className="metric-label">Battery Health</span>
          <strong className={healthClass}>
            {battery.bhi}
          </strong>
          <span className="out-of">/100</span>
        </div>

        <div className="health-bar">
          <div
            className={healthClass}
            style={{ width: `${battery.bhi}%` }}
          />
        </div>
      </div>

      <div className="card-bottom">
        <div>
          <span>RUL</span>
          <strong>{battery.rul_days} days</strong>
        </div>

        <div>
          <span>Failure Risk</span>
          <strong>{battery.risk_pct}%</strong>
        </div>
      </div>
    </Link>
  );
}