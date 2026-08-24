import { getBattery, getExplanation } from "@/lib/api";
import HealthGauge from "@/components/HealthGauge";
import HealthChart from "@/components/HealthChart";
import WhyPanel from "@/components/WhyPanel";
import WhatIfPanel from "@/components/WhatIfPanel";
import RiskBadge from "@/components/RiskBadge";

interface Props {
  params: {
    id: string;
  };
}

export default async function BatteryPage({
  params,
}: Props) {
  const battery = await getBattery(params.id);
  const explanation = await getExplanation(params.id);

  return (
    <div>
      <header className="detail-header">
        <div>
          <p className="eyebrow">{battery.id}</p>

          <h2>{battery.name}</h2>

          <p className="page-description">
            {battery.vehicle_type} · Installed{" "}
            {battery.install_date}
          </p>
        </div>

        <RiskBadge risk={battery.risk_pct} />
      </header>

      <div className="detail-grid">
        <div className="panel health-panel">
          <div className="panel-header">
            <div>
              <span className="panel-kicker">
                BATTERY HEALTH INDEX
              </span>

              <h3>Current Health</h3>
            </div>
          </div>

          <HealthGauge value={battery.bhi} />

          <div className="prediction-cards">
            <div>
              <span>Remaining Useful Life</span>
              <strong>{battery.rul_days} days</strong>
            </div>

            <div>
              <span>90-Day Failure Risk</span>
              <strong>{battery.risk_pct}%</strong>
            </div>
          </div>
        </div>

        <div className="panel">
          <div className="panel-header">
            <div>
              <span className="panel-kicker">
                TELEMETRY-DERIVED HEALTH
              </span>

              <h3>Capacity Trend</h3>
            </div>
          </div>

          <HealthChart data={battery.telemetry} />
        </div>
      </div>

      <div className="detail-grid">
        <WhyPanel explanation={explanation} />

        <div className="panel">
          <div className="panel-header">
            <div>
              <span className="panel-kicker">
                MODEL PREDICTION
              </span>

              <h3>Failure Forecast</h3>
            </div>
          </div>

          <div className="forecast-number">
            {battery.risk_pct}%
          </div>

          <p>
            Estimated probability of battery failure within
            the next 90 days.
          </p>

          <div className="risk-meter">
            <div
              style={{
                width: `${battery.risk_pct}%`,
              }}
            />
          </div>
        </div>
      </div>

      <WhatIfPanel batteryId={battery.id} />
    </div>
  );
}