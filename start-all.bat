@echo off
title TrafficVision AI Launcher
echo =================================================================
echo          TrafficVision AI -- Full System Launch Manager
echo =================================================================

set UVICORN=c:\trafficvision\aibin-backend\.venv\Scripts\uvicorn.exe

if exist "c:\trafficvision\hariom-frontend\frontend\.next" (
    rmdir /s /q "c:\trafficvision\hariom-frontend\frontend\.next" >nul 2>&1
)

echo [1/6] Launching Traffic Monitoring Service (Port 8000)...
start "Data Service (8000)" /D "c:\trafficvision\anmol-data" cmd /k ""%UVICORN%" Api.traffic_api:app --host 127.0.0.1 --port 8000 --reload"

echo [2/6] Launching AI / ML Prediction Engine (Port 8001)...
start "AI Engine (8001)" /D "c:\trafficvision\saksham-aiml" cmd /k ""%UVICORN%" ai_engine.main:app --host 127.0.0.1 --port 8001 --reload"

echo [3/6] Launching Route Analysis Service (Port 8002)...
start "Route Analysis (8002)" /D "c:\trafficvision\aibin-backend" cmd /k ""%UVICORN%" route_analysis.main:app --host 127.0.0.1 --port 8002 --reload"

echo [4/6] Launching Alert Microservice (Port 8003)...
start "Alert Service (8003)" /D "c:\trafficvision\aibin-backend" cmd /k ""%UVICORN%" alert_service.main:app --host 127.0.0.1 --port 8003 --reload"

echo [5/6] Launching API Gateway and Auth Service (Port 8080)...
start "API Gateway (8080)" /D "c:\trafficvision\aibin-backend" cmd /k ""%UVICORN%" app.main:app --host 127.0.0.1 --port 8080 --reload"

echo [6/6] Launching Hariom's Next.js Frontend (Port 3000)...
start "Frontend (3000)" /D "c:\trafficvision\hariom-frontend\frontend" cmd /k "npm run dev"

echo.
echo =================================================================
echo All services initiated!
echo   - Frontend:    http://localhost:3000
echo   - Gateway:     http://localhost:8080/docs
echo   - Data API:    http://localhost:8000/docs
echo   - AI Engine:   http://localhost:8001/docs
echo   - Routes:      http://localhost:8002/docs
echo   - Alerts:      http://localhost:8003/docs
echo =================================================================
