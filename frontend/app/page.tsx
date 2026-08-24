import { getBatteries } from "@/lib/api";
import BatteryCard from "@/components/BatteryCard";
import FleetStats from "@/components/FleetStats";

export default async function HomePage() {
  const batteries = await getBatteries();

  const sorted = [...batteries].sort(
    (a, b) => b.risk_pct - a.risk_pct
  );

  return (
    <div>
      <header className="page-header">
        <div>
          <p className="eyebrow">BATTERY DIGITAL TWIN</p>
          <h2>Fleet Risk Intelligence</h2>
          <p className="page-description">
            Identify which batteries need attention before
            failure becomes downtime.
          </p>
        </div>

        <div className="live-status">
          <span />
          LIVE MONITORING
        </div>
      </header>

      <FleetStats batteries={batteries} />

      <section className="risk-section">
        <div className="section-heading">
          <div>
            <h3>Risk Priority</h3>
            <p>
              Batteries ranked by predicted 90-day failure
              probability
            </p>
          </div>

          <span className="asset-count">
            {batteries.length} assets
          </span>
        </div>

        <div className="battery-grid">
          {sorted.map((battery) => (
            <BatteryCard
              key={battery.id}
              battery={battery}
            />
          ))}
        </div>
      </section>
    </div>
  );
}