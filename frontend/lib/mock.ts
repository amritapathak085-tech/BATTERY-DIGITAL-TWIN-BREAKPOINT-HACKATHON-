import {
  Battery,
  BatteryDetail,
  ExplanationResponse,
} from "./types";

export const mockBatteries: Battery[] = [
  {
    id: "BAT-001",
    name: "EV-01",
    vehicle_type: "Heavy Freight",
    bhi: 42,
    rul_days: 47,
    risk_pct: 81,
  },
  {
    id: "BAT-002",
    name: "EV-02",
    vehicle_type: "Mining",
    bhi: 58,
    rul_days: 91,
    risk_pct: 52,
  },
  {
    id: "BAT-003",
    name: "EV-03",
    vehicle_type: "Plant Logistics",
    bhi: 76,
    rul_days: 164,
    risk_pct: 21,
  },
  {
    id: "BAT-004",
    name: "EV-04",
    vehicle_type: "Construction",
    bhi: 89,
    rul_days: 241,
    risk_pct: 8,
  },
  {
    id: "BAT-005",
    name: "EV-05",
    vehicle_type: "Heavy Freight",
    bhi: 35,
    rul_days: 31,
    risk_pct: 91,
  },
  {
    id: "BAT-006",
    name: "EV-06",
    vehicle_type: "Mining",
    bhi: 68,
    rul_days: 128,
    risk_pct: 32,
  },
  {
    id: "BAT-007",
    name: "EV-07",
    vehicle_type: "Plant Logistics",
    bhi: 82,
    rul_days: 198,
    risk_pct: 14,
  },
  {
    id: "BAT-008",
    name: "EV-08",
    vehicle_type: "Construction",
    bhi: 73,
    rul_days: 153,
    risk_pct: 26,
  },
  {
    id: "BAT-009",
    name: "EV-09",
    vehicle_type: "Heavy Freight",
    bhi: 47,
    rul_days: 62,
    risk_pct: 73,
  },
  {
    id: "BAT-010",
    name: "EV-10",
    vehicle_type: "Mining",
    bhi: 93,
    rul_days: 286,
    risk_pct: 4,
  },
  {
    id: "BAT-011",
    name: "EV-11",
    vehicle_type: "Plant Logistics",
    bhi: 61,
    rul_days: 104,
    risk_pct: 44,
  },
  {
    id: "BAT-012",
    name: "EV-12",
    vehicle_type: "Construction",
    bhi: 78,
    rul_days: 176,
    risk_pct: 18,
  },
  {
    id: "BAT-013",
    name: "EV-13",
    vehicle_type: "Heavy Freight",
    bhi: 51,
    rul_days: 73,
    risk_pct: 66,
  },
  {
    id: "BAT-014",
    name: "EV-14",
    vehicle_type: "Mining",
    bhi: 87,
    rul_days: 225,
    risk_pct: 9,
  },
  {
    id: "BAT-015",
    name: "EV-15",
    vehicle_type: "Plant Logistics",
    bhi: 69,
    rul_days: 137,
    risk_pct: 29,
  },
  {
    id: "BAT-016",
    name: "EV-16",
    vehicle_type: "Construction",
    bhi: 94,
    rul_days: 301,
    risk_pct: 3,
  },
  {
    id: "BAT-017",
    name: "EV-17",
    vehicle_type: "Heavy Freight",
    bhi: 56,
    rul_days: 82,
    risk_pct: 58,
  },
  {
    id: "BAT-018",
    name: "EV-18",
    vehicle_type: "Mining",
    bhi: 74,
    rul_days: 151,
    risk_pct: 24,
  },
  {
    id: "BAT-019",
    name: "EV-19",
    vehicle_type: "Plant Logistics",
    bhi: 39,
    rul_days: 38,
    risk_pct: 87,
  },
  {
    id: "BAT-020",
    name: "EV-20",
    vehicle_type: "Construction",
    bhi: 84,
    rul_days: 213,
    risk_pct: 12,
  },
];

export function getMockBattery(id: string): BatteryDetail {
  const battery =
    mockBatteries.find((item) => item.id === id) || mockBatteries[0];

  const telemetry = Array.from({ length: 90 }, (_, index) => {
    const day = index + 1;
    const degradation = day * 0.025;

    return {
      day,
      voltage: Number((400 - degradation * 0.7).toFixed(2)),
      temperature: Number((32 + Math.sin(day / 8) * 5 + degradation).toFixed(2)),
      cycle_count: Math.round(day * 1.7),
      depth_of_discharge: Number(
        (70 + Math.sin(day / 10) * 8).toFixed(2)
      ),
      fast_charge_freq: Number(
        (3 + Math.sin(day / 7) * 1.5 + degradation / 10).toFixed(2)
      ),
      capacity_pct: Number((100 - degradation).toFixed(2)),
    };
  });

  return {
    ...battery,
    install_date: "2025-08-01",
    telemetry,
  };
}

export function getMockExplanation(): ExplanationResponse {
  return {
    reasons: [
      {
        feature: "Temperature Exposure",
        impact: 0.42,
        plain_english:
          "High average temperature is accelerating battery degradation.",
      },
      {
        feature: "Fast-Charge Frequency",
        impact: 0.31,
        plain_english:
          "Frequent fast charging is increasing stress on the battery cells.",
      },
      {
        feature: "Depth of Discharge",
        impact: 0.18,
        plain_english:
          "Deep discharge cycles are contributing to faster capacity loss.",
      },
      {
        feature: "Cycle Count",
        impact: 0.09,
        plain_english:
          "Higher cumulative cycling indicates increased battery wear.",
      },
    ],
  };
}