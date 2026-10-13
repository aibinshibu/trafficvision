# TrafficVision AI — Automated Service Launcher (Windows PowerShell)
# Launches all 5 backend microservices and Hariom's Next.js frontend in separate terminal windows.

$VENV_UVICORN = "c:\trafficvision\aibin-backend\.venv\Scripts\uvicorn.exe"
$NPX = if (Test-Path "C:\Program Files\nodejs\npx.cmd") { "C:\Program Files\nodejs\npx.cmd" } else { "npx" }

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "         TrafficVision AI -- Full System Launch Manager           " -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

# 1. Anmol's Data Service (Port 8000)
Write-Host "[1/6] Launching Traffic Monitoring and Analytics Service (Port 8000)..." -ForegroundColor Yellow
Start-Process powershell -WorkingDirectory "c:\trafficvision\anmol-data" -ArgumentList "-NoExit", "-Command", "& '$VENV_UVICORN' Api.traffic_api:app --host 127.0.0.1 --port 8000 --reload"

# 2. Saksham's AI Engine (Port 8001)
Write-Host "[2/6] Launching AI / ML Prediction Engine (Port 8001)..." -ForegroundColor Yellow
Start-Process powershell -WorkingDirectory "c:\trafficvision\saksham-aiml" -ArgumentList "-NoExit", "-Command", "& '$VENV_UVICORN' ai_engine.main:app --host 127.0.0.1 --port 8001 --reload"

# 3. Route Analysis Service (Port 8002)
Write-Host "[3/6] Launching Route Analysis Service (Port 8002)..." -ForegroundColor Yellow
Start-Process powershell -WorkingDirectory "c:\trafficvision\aibin-backend" -ArgumentList "-NoExit", "-Command", "& '$VENV_UVICORN' route_analysis.main:app --host 127.0.0.1 --port 8002 --reload"

# 4. Alert Service (Port 8003)
Write-Host "[4/6] Launching Alert Microservice (Port 8003)..." -ForegroundColor Yellow
Start-Process powershell -WorkingDirectory "c:\trafficvision\aibin-backend" -ArgumentList "-NoExit", "-Command", "& '$VENV_UVICORN' alert_service.main:app --host 127.0.0.1 --port 8003 --reload"

# 5. API Gateway (Port 8080)
Write-Host "[5/6] Launching API Gateway and Auth Service (Port 8080)..." -ForegroundColor Yellow
Start-Process powershell -WorkingDirectory "c:\trafficvision\aibin-backend" -ArgumentList "-NoExit", "-Command", "& '$VENV_UVICORN' app.main:app --host 127.0.0.1 --port 8080 --reload"

# 6. Hariom's Frontend (Port 3000)
Write-Host "[6/6] Launching Hariom's Next.js Frontend (Port 3000)..." -ForegroundColor Yellow
Start-Process powershell -WorkingDirectory "c:\trafficvision\hariom-frontend\frontend" -ArgumentList "-NoExit", "-Command", "& '$NPX' next dev -p 3000"

Write-Host ""
Write-Host "=================================================================" -ForegroundColor Green
Write-Host "All services initiated successfully!" -ForegroundColor Green
Write-Host "  - Frontend:    http://localhost:3000" -ForegroundColor White
Write-Host "  - Gateway:     http://localhost:8080/docs" -ForegroundColor White
Write-Host "  - Data API:    http://localhost:8000/docs" -ForegroundColor White
Write-Host "  - AI Engine:   http://localhost:8001/docs" -ForegroundColor White
Write-Host "  - Routes:      http://localhost:8002/docs" -ForegroundColor White
Write-Host "  - Alerts:      http://localhost:8003/docs" -ForegroundColor White
Write-Host "=================================================================" -ForegroundColor Green
