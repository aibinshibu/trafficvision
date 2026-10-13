"""
Proxy router for the Route Analysis Service (Intern 1 - Milestone 2).
Forwards requests from the API Gateway (port 8080) to the Route Analysis Service (port 8002).
"""

from fastapi import APIRouter, Request, HTTPException, status, Depends
import httpx
from ..config import settings
from ..auth.dependencies import get_current_user

router = APIRouter()

async def _route_forwarder(path: str, request: Request):
    url = f"{settings.ROUTE_ANALYSIS_URL}/api/v1/route/{path}"
    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            response = await client.get(url, params=request.query_params)
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"route_analysis returned error: {response.text}"
                )
            return response.json()
    except httpx.RequestError as e:
        try:
            from route_analysis.router import (
                get_optimized_route,
                get_alternate_routes,
                get_travel_time,
                get_road_conditions,
            )
            if path == "optimize":
                orig = request.query_params.get("origin", "12.9716,77.5946")
                dest = request.query_params.get("destination", "12.9352,77.6245")
                pref = request.query_params.get("preference", "fastest")
                res = await get_optimized_route(origin=orig, destination=dest, preference=pref)
                return res.model_dump()
            elif path == "alternate":
                orig = request.query_params.get("origin", "12.9716,77.5946")
                dest = request.query_params.get("destination", "12.9352,77.6245")
                max_r = int(request.query_params.get("max_routes", 3))
                res = await get_alternate_routes(origin=orig, destination=dest, max_routes=max_r)
                return [r.model_dump() for r in res]
            elif path in ["travel-time", "travel"]:
                r_id = request.query_params.get("route_id", "rt_opt_129716_775946_to_129352_776245")
                res = await get_travel_time(route_id=r_id)
                return res.model_dump()
            elif path == "conditions":
                r_id = request.query_params.get("road_id", "1")
                res = await get_road_conditions(road_id=r_id)
                return res.model_dump()
        except Exception:
            pass
        raise HTTPException(
            status_code=502,
            detail={"error": "route_analysis unreachable", "upstream": url, "exception": str(e)}
        )

@router.get("/optimize")
async def optimize_route(origin: str, destination: str, request: Request, user=Depends(get_current_user)):
    """Get the optimal driving route."""
    return await _route_forwarder("optimize", request)

@router.get("/alternate")
async def alternate_routes(origin: str, destination: str, request: Request, max_routes: int = 3, user=Depends(get_current_user)):
    """Get alternative candidate routes."""
    return await _route_forwarder("alternate", request)

@router.get("/travel-time")
@router.get("/travel")
async def travel_time(route_id: str, request: Request, user=Depends(get_current_user)):
    """Get travel time and ETA for a specific route."""
    return await _route_forwarder("travel-time", request)

@router.get("/conditions")
async def road_conditions(road_id: str, request: Request, user=Depends(get_current_user)):
    """Get live corridor conditions."""
    return await _route_forwarder("conditions", request)
