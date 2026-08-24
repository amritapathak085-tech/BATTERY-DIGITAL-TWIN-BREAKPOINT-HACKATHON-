import {
  Battery,
  BatteryDetail,
  ExplanationResponse,
  WhatIfRequest,
  WhatIfResponse,
} from "./types";

import {
  mockBatteries,
  getMockBattery,
  getMockExplanation,
} from "./mock";

const MOCK = process.env.NEXT_PUBLIC_MOCK === "true";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers || {}),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return response.json();
}

export async function getBatteries(): Promise<Battery[]> {
  if (MOCK) {
    return mockBatteries;
  }

  return request<Battery[]>("/batteries");
}

export async function getBattery(
  id: string
): Promise<BatteryDetail> {
  if (MOCK) {
    return getMockBattery(id);
  }

  return request<BatteryDetail>(`/batteries/${id}`);
}

export async function getExplanation(
  id: string
): Promise<ExplanationResponse> {
  if (MOCK) {
    return getMockExplanation();
  }

  return request<ExplanationResponse>(
    `/batteries/${id}/explain`
  );
}

export async function runWhatIf(
  id: string,
  data: WhatIfRequest
): Promise<WhatIfResponse> {
  if (MOCK) {
    const battery = mockBatteries.find((b) => b.id === id);

    const before = {
      bhi: battery?.bhi || 60,
      rul_days: battery?.rul_days || 100,
      failure_risk_pct: battery?.risk_pct || 40,
    };

    const improvement =
      (90 - data.charge_cap_pct) * 0.15 +
      (100 - data.duty_cycle_pct) * 0.08 +
      Math.max(0, 40 - data.ambient_temp_c) * 0.1;

    const after = {
      bhi: Math.min(100, Math.round(before.bhi + improvement)),
      rul_days: Math.round(before.rul_days + improvement * 3),
      failure_risk_pct: Math.max(
        1,
        Math.round(before.failure_risk_pct - improvement)
      ),
    };

    return {
      before,
      after,
      savings: {
        inr: Math.round(improvement * 18500),
        downtime_days: Number((improvement * 0.12).toFixed(1)),
        co2_kg: Math.round(improvement * 28),
      },
    };
  }

  return request<WhatIfResponse>(
    `/batteries/${id}/whatif`,
    {
      method: "POST",
      body: JSON.stringify(data),
    }
  );
}