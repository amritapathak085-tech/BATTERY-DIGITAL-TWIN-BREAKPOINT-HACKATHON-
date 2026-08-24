import { Battery } from "@/lib/types";

export default function FleetStats({
  batteries,
}: {
  batteries: Battery[];
}) {
  const critical = batteries.filter(
    (battery) => battery.risk_pct >= 70
  ).length;

  const avgHealth = Math.round(
    batteries.reduce((sum, battery) => sum + battery.bhi, 0) /
      batteries.length
  );

  const avgRul = Math.round(
    batteries.reduce(
      (sum, battery) => sum + battery.rul_days,
      0
    ) / batteries.length
  );

  return (
    <div className="stats-grid">
      <div className="stat-card">
        <span>Fleet Batteries</span>
        <strong>{batteries.length}</strong>
        <small>Monitored assets</small>
      </div>

      <div className="stat-card danger-stat">
        <span>Critical Risk</span>
        <strong>{critical}</strong>
        <small>Require attention</small>
      </div>

      <div className="stat-card">
        <span>Avg. Battery Health</span>
        <strong>{avgHealth}</strong>
        <small>Out of 100</small>
      </div>

      <div className="stat-card">
        <span>Avg. RUL</span>
        <strong>{avgRul}</strong>
        <small>Days remaining</small>
      </div>
    </div>
  );
}