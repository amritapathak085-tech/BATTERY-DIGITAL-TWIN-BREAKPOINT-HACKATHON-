"use client";

import { useState } from "react";
import { runWhatIf } from "@/lib/api";
import { WhatIfResponse } from "@/lib/types";

export default function WhatIfPanel({
  batteryId,
}: {
  batteryId: string;
}) {
  const [chargeCap, setChargeCap] = useState(80);
  const [dutyCycle, setDutyCycle] = useState(70);
  const [temperature, setTemperature] = useState(35);

  const [result, setResult] =
    useState<WhatIfResponse | null>(null);

  const [loading, setLoading] = useState(false);

  async function simulate() {
    setLoading(true);

    try {
      const response = await runWhatIf(batteryId, {
        charge_cap_pct: chargeCap,
        duty_cycle_pct: dutyCycle,
        ambient_temp_c: temperature,
      });

      setResult(response);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="panel simulation-panel">
      <div className="panel-header">
        <div>
          <span className="panel-kicker">
            COUNTERFACTUAL SIMULATION
          </span>

          <h3>What if we change operations?</h3>

          <p>
            Modify operating conditions and simulate the
            predicted consequence.
          </p>
        </div>
      </div>

      <div className="slider-list">
        <label>
          <div>
            <span>Charge Cap</span>
            <strong>{chargeCap}%</strong>
          </div>

          <input
            type="range"
            min="60"
            max="100"
            value={chargeCap}
            onChange={(e) =>
              setChargeCap(Number(e.target.value))
            }
          />
        </label>

        <label>
          <div>
            <span>Duty Cycle</span>
            <strong>{dutyCycle}%</strong>
          </div>

          <input
            type="range"
            min="40"
            max="100"
            value={dutyCycle}
            onChange={(e) =>
              setDutyCycle(Number(e.target.value))
            }
          />
        </label>

        <label>
          <div>
            <span>Ambient Temperature</span>
            <strong>{temperature}°C</strong>
          </div>

          <input
            type="range"
            min="20"
            max="50"
            value={temperature}
            onChange={(e) =>
              setTemperature(Number(e.target.value))
            }
          />
        </label>
      </div>

      <button
        className="simulate-button"
        onClick={simulate}
        disabled={loading}
      >
        {loading
          ? "Running simulation..."
          : "Run What-If Simulation"}
      </button>

      {result && (
        <div className="simulation-result">
          <div className="comparison">
            <div>
              <span>Before</span>
              <strong>
                {result.before.rul_days} days
              </strong>
              <small>
                RUL · {result.before.failure_risk_pct}% risk
              </small>
            </div>

            <div className="arrow">→</div>

            <div className="after">
              <span>After</span>
              <strong>
                {result.after.rul_days} days
              </strong>
              <small>
                RUL · {result.after.failure_risk_pct}% risk
              </small>
            </div>
          </div>

          <div className="impact-grid">
            <div>
              <span>₹ Savings</span>
              <strong>
                ₹{result.savings.inr.toLocaleString("en-IN")}
              </strong>
            </div>

            <div>
              <span>Downtime Avoided</span>
              <strong>
                {result.savings.downtime_days} days
              </strong>
            </div>

            <div>
              <span>CO₂ Impact</span>
              <strong>
                {result.savings.co2_kg} kg
              </strong>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}