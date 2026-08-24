from datetime import date, datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class Battery(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    vehicle_type: str
    install_date: date


class Telemetry(BaseModel):
    battery_id: str
    day: date
    voltage: float
    temperature: float
    cycle_count: int
    depth_of_discharge: float
    fast_charge_freq: float
    capacity_pct: float


class Prediction(BaseModel):
    battery_id: str
    bhi: float
    rul_days: float
    failure_risk_pct: float
    computed_at: datetime


class BatterySummary(Battery):
    bhi: float | None = None
    rul_days: float | None = None
    failure_risk_pct: float | None = None
    computed_at: datetime | None = None


class PredictResponse(Prediction):
    pass


class ExplainResponse(BaseModel):
    battery_id: str
    explanation: Any


class WhatIfRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    voltage: float | None = None
    temperature: float | None = None
    cycle_count: int | None = None
    depth_of_discharge: float | None = None
    fast_charge_freq: float | None = None
    capacity_pct: float | None = None
    horizon_days: int | None = Field(default=None, ge=1)


class WhatIfResponse(BaseModel):
    battery_id: str
    result: Any
