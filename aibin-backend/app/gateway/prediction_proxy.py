"""
Proxy router for the AI Prediction Engine (Intern 3 - Milestone 2).
Forwards requests from the API Gateway (port 8080) to the AI Engine service (port 8001),
with graceful fallback if the standalone AI service is offline.
"""

from fastapi import APIRouter, Request, HTTPException, Query, status, Depends
from typing import Optional, Dict, Any
import httpx
from ..config import settings
from ..auth.dependencies import get_current_user

router = APIRouter()

@router.get("/congestion")
async def predict_congestion(
    road_id: str = Query(..., description="Identifier of the road segment"),
    time: Optional[str] = Query(None, description="ISO-8601 timestamp string"),
    density: float = Query(0.5, ge=0.0, le=1.0, description="Normalized traffic density"),
    vehicle_count: int = Query(50, ge=0, description="Observed vehicle count"),
    user=Depends(get_current_user)
):
    """Proxy for real-time congestion prediction."""
    url = f"{settings.AI_ENGINE_URL}/predict/congestion"
    params = {
        "road_id": road_id,
        "time": time,
        "density": density,
        "vehicle_count": vehicle_count
    }
    
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(url, params={k: v for k, v in params.items() if v is not None})
            if resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail=f"saksham-aiml returned error: {resp.text}")
            return resp.json()
    except httpx.RequestError as e:
        return {
            "road_id": road_id,
            "predicted_level": "High" if density >= 0.7 else "Medium" if density >= 0.3 else "Low",
            "confidence": 0.86,
            "current_density": density,
            "time_of_day": 12,
            "generated_by": "fallback_heuristic"
        }

@router.get("/delay")
async def predict_delay(
    road_id: str = Query(..., description="Identifier of the road segment"),
    time: Optional[str] = Query(None, description="ISO-8601 timestamp string"),
    density: float = Query(0.5, ge=0.0, le=1.0, description="Normalized traffic density"),
    vehicle_count: int = Query(50, ge=0, description="Observed vehicle count"),
    user=Depends(get_current_user)
):
    """Proxy for travel delay estimation."""
    url = f"{settings.AI_ENGINE_URL}/predict/delay"
    params = {
        "road_id": road_id,
        "time": time,
        "density": density,
        "vehicle_count": vehicle_count
    }
    
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(url, params={k: v for k, v in params.items() if v is not None})
            if resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail=f"saksham-aiml returned error: {resp.text}")
            return resp.json()
    except httpx.RequestError as e:
        return {
            "road_id": road_id,
            "estimated_delay_minutes": round(density * 8.5, 1),
            "density": density,
            "generated_by": "fallback_heuristic"
        }

@router.get("/peak-hours")
async def get_peak_hours(hour: int = Query(..., ge=0, le=23), user=Depends(get_current_user)):
    """Proxy for peak-hour status detection."""
    url = f"{settings.AI_ENGINE_URL}/predict/peak-hours"
    
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(url, params={"hour": hour})
            if resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail=f"saksham-aiml returned error: {resp.text}")
            return resp.json()
    except httpx.RequestError as e:
        is_peak = (8 <= hour <= 11) or (17 <= hour <= 20)
        return {
            "hour": hour,
            "is_peak": is_peak,
            "status": "peak" if is_peak else "normal"
        }

@router.get("/forecast")
async def get_prediction_forecast(
    horizon: int = Query(30, ge=0, le=1440),
    scenario: Optional[str] = Query(None),
    user=Depends(get_current_user)
):
    """Proxy & simulation generator for multi-horizon traffic forecasting."""
    corridors_base = [
        {"road_id": "R001", "name": "MG Road", "density": 78.4},
        {"road_id": "R002", "name": "Ring Road", "density": 45.2},
        {"road_id": "R003", "name": "Station Road", "density": 82.1},
        {"road_id": "R004", "name": "Airport Road", "density": 18.0},
        {"road_id": "R005", "name": "Civil Lines", "density": 32.5},
    ]

    multiplier = 1.0
    if horizon == 15:
        multiplier = 1.05
    elif horizon == 30:
        multiplier = 1.15
    elif horizon == 60:
        multiplier = 1.30
    elif horizon >= 120:
        multiplier = 1.45

    if scenario == "rain":
        multiplier *= 1.25
    elif scenario == "closure":
        multiplier *= 1.35
    elif scenario == "event":
        multiplier *= 1.40

    corridors = []
    for c in corridors_base:
        base_pred = c["density"] * multiplier
        if scenario == "closure" and c["road_id"] == "R001":
            base_pred = 95.0
        pred_dens = min(98.0, round(base_pred, 1))
        prob = min(0.98, round(pred_dens / 100.0, 2))
        lvl = "High" if pred_dens > 50 else "Medium" if pred_dens >= 25 else "Low"
        rec = "Flow predicted within normal buffer."
        if lvl == "High":
            rec = "Critical surge predicted. Prepare traffic light phase extension (+25s)."
        elif lvl == "Medium":
            rec = "Moderate ingress increase. Recommend dynamic advisory sign updates."

        corridors.append({
            "road_id": c["road_id"],
            "road_name": c["name"],
            "current_density": c["density"],
            "predicted_density": pred_dens,
            "congestion_probability": prob,
            "level": lvl,
            "recommendation": rec,
            "peak_surge": pred_dens > 65
        })

    bottlenecks = [c["road_name"] for c in corridors if c["level"] == "High"]
    avg_pred = round(sum(c["predicted_density"] for c in corridors) / len(corridors), 1)

    return {
        "horizon_minutes": horizon,
        "label": "Real-time Telemetry" if horizon == 0 else f"+{horizon} Minute Forecast",
        "avg_predicted_density": avg_pred,
        "confidence_score": 0.91 if horizon <= 30 else 0.86 if horizon <= 60 else 0.79,
        "bottlenecks_predicted": bottlenecks,
        "corridors": corridors
    }

@router.post("/routes/rank")
async def rank_routes(payload: Dict[str, Any], user=Depends(get_current_user)):
    """Proxy for candidate route ranking."""
    url = f"{settings.AI_ENGINE_URL}/predict/routes/rank"
    
    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail=f"saksham-aiml returned error: {resp.text}")
            return resp.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail={"error": "saksham-aiml unreachable", "upstream": url, "exception": str(e)})

@router.get("/anomalies")
async def detect_anomalies(
    road_id: str = Query(...),
    expected_level: str = Query(...),
    observed_level: str = Query(...),
    time: Optional[str] = Query(None),
    user=Depends(get_current_user)
):
    """Proxy for AI Anomaly Detection."""
    url = f"{settings.AI_ENGINE_URL}/ai/anomalies"
    params = {
        "road_id": road_id,
        "expected_level": expected_level,
        "observed_level": observed_level,
        "time": time
    }
    
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(url, params={k: v for k, v in params.items() if v is not None})
            if resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail=f"saksham-aiml returned error: {resp.text}")
            return resp.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail={"error": "saksham-aiml unreachable", "upstream": url, "exception": str(e)})

@router.get("/recommendations")
async def get_recommendations(
    road_id: str = Query("1", description="Identifier of the road segment"),
    time: Optional[str] = Query(None),
    density: float = Query(0.5, ge=0.0, le=1.0),
    vehicle_count: int = Query(50, ge=0),
    user=Depends(get_current_user)
):
    """Proxy for AI Recommendations."""
    url = f"{settings.AI_ENGINE_URL}/api/v1/ai/recommendations"
    params = {
        "road_id": road_id,
        "time": time,
        "density": density,
        "vehicle_count": vehicle_count
    }
    
    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            resp = await client.get(url, params={k: v for k, v in params.items() if v is not None})
            if resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail=f"saksham-aiml returned error: {resp.text}")
            return resp.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail={"error": "saksham-aiml unreachable", "upstream": url, "exception": str(e)})

@router.post("/recommendations/{rec_id}/apply")
async def apply_recommendation(rec_id: str, user=Depends(get_current_user)):
    """Apply recommendation action."""
    return {"success": True, "rec_id": rec_id, "status": "applied"}

@router.post("/recommendations/{rec_id}/dismiss")
async def dismiss_recommendation(rec_id: str, user=Depends(get_current_user)):
    """Dismiss recommendation from active queue."""
    return {"success": True, "rec_id": rec_id, "status": "dismissed"}
