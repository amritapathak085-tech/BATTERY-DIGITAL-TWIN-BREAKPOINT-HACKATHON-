from datetime import datetime, timezone
import importlib
from fastapi import APIRouter, HTTPException

from backend.db import table
from backend.schemas import (
    BatterySummary,
    ExplainResponse,
    PredictResponse,
    Telemetry,
    WhatIfRequest,
    WhatIfResponse,
)

router = APIRouter(prefix="/batteries", tags=["batteries"])


def _latest_prediction(battery_id: str):
    result = (
        table("predictions")
        .select("battery_id,bhi,rul_days,failure_risk_pct,computed_at")
        .eq("battery_id", battery_id)
        .order("computed_at", desc=True)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


def _battery_or_404(battery_id: str):
    result = table("batteries").select("id,vehicle_type,install_date").eq("id", battery_id).limit(1).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail=f"Battery '{battery_id}' not found")
    return result.data[0]


def _telemetry(battery_id: str):
    result = (
        table("telemetry")
        .select("battery_id,day,voltage,temperature,cycle_count,depth_of_discharge,fast_charge_freq,capacity_pct")
        .eq("battery_id", battery_id)
        .order("day", desc=False)
        .execute()
    )
    return result.data


def _call_ml(module_name: str, function_name: str, payload: dict):
    """Adapter for Amrita's ML modules.

    Expected contract: ml/<module>.py exposes a callable named <function_name>
    accepting one dictionary and returning JSON-serializable data.
    """
    try:
        module = importlib.import_module(f"ml.{module_name}")
    except ModuleNotFoundError as exc:
        raise HTTPException(status_code=503, detail=f"ML module ml/{module_name}.py is not available") from exc
    fn = getattr(module, function_name, None)
    if not callable(fn):
        raise HTTPException(
            status_code=500,
            detail=f"ml/{module_name}.py must expose {function_name}(payload)",
        )
    try:
        return fn(payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"ML module {module_name} failed: {exc}") from exc


@router.get("", response_model=list[BatterySummary])
def list_batteries():
    batteries = table("batteries").select("id,vehicle_type,install_date").order("id").execute().data
    output = []
    for battery in batteries:
        prediction = _latest_prediction(battery["id"])
        output.append({**battery, **(prediction or {})})
    return output


@router.get("/{battery_id}", response_model=list[Telemetry])
def get_battery_history(battery_id: str):
    _battery_or_404(battery_id)
    return _telemetry(battery_id)


@router.get("/{battery_id}/predict", response_model=PredictResponse)
def predict_battery(battery_id: str):
    _battery_or_404(battery_id)
    history = _telemetry(battery_id)
    if not history:
        raise HTTPException(status_code=404, detail="No telemetry found for this battery")

    result = _call_ml("predict", "predict_battery", {"battery_id": battery_id, "telemetry": history})
    required = ("bhi", "rul_days", "failure_risk_pct")
    missing = [key for key in required if key not in result]
    if missing:
        raise HTTPException(status_code=500, detail=f"Prediction missing fields: {missing}")

    row = {
        "battery_id": battery_id,
        "bhi": result["bhi"],
        "rul_days": result["rul_days"],
        "failure_risk_pct": result["failure_risk_pct"],
        "computed_at": datetime.now(timezone.utc).isoformat(),
    }
    saved = table("predictions").insert(row).execute().data[0]
    return saved


@router.get("/{battery_id}/explain", response_model=ExplainResponse)
def explain_battery(battery_id: str):
    _battery_or_404(battery_id)
    history = _telemetry(battery_id)
    prediction = _latest_prediction(battery_id)
    result = _call_ml(
        "explain",
        "explain_battery",
        {"battery_id": battery_id, "telemetry": history, "prediction": prediction},
    )
    return {"battery_id": battery_id, "explanation": result}


@router.post("/{battery_id}/whatif", response_model=WhatIfResponse)
def battery_whatif(battery_id: str, request: WhatIfRequest):
    _battery_or_404(battery_id)
    history = _telemetry(battery_id)
    latest = history[-1] if history else None
    if latest is None:
        raise HTTPException(status_code=404, detail="No telemetry found for this battery")

    modified = {**latest, **request.model_dump(exclude_none=True)}
    result = _call_ml(
        "simulate",
        "simulate_battery",
        {"battery_id": battery_id, "baseline": latest, "modified_inputs": modified, "telemetry": history},
    )
    return {"battery_id": battery_id, "result": result}
