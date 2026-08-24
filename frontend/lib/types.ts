export interface Battery {
  id: string;
  name: string;
  vehicle_type: string;
  bhi: number;
  rul_days: number;
  risk_pct: number;
}

export interface TelemetryPoint {
  day: number;
  voltage: number;
  temperature: number;
  cycle_count: number;
  depth_of_discharge: number;
  fast_charge_freq: number;
  capacity_pct: number;
}

export interface BatteryDetail extends Battery {
  install_date: string;
  telemetry: TelemetryPoint[];
}

export interface Reason {
  feature: string;
  impact: number;
  plain_english: string;
}

export interface ExplanationResponse {
  reasons: Reason[];
}

export interface Prediction {
  bhi: number;
  rul_days: number;
  failure_risk_pct: number;
}

export interface WhatIfRequest {
  charge_cap_pct: number;
  duty_cycle_pct: number;
  ambient_temp_c: number;
}

export interface WhatIfResponse {
  before: Prediction;
  after: Prediction;
  savings: {
    inr: number;
    downtime_days: number;
    co2_kg: number;
  };
}