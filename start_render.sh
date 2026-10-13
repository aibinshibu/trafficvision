#!/usr/bin/env bash
# TrafficVision AI — Render Production Startup Script
# Starts all internal microservices in the background, then runs the API Gateway on Render's assigned $PORT.

set -e

echo "=========================================================="
echo "      TrafficVision AI -- Render Production Launcher       "
echo "=========================================================="

ROOT_DIR="$(pwd)"
PORT="${PORT:-10000}"

echo "[1/5] Launching Traffic Monitoring Service (Port 8000)..."
(cd "$ROOT_DIR/anmol-data" && uvicorn Api.traffic_api:app --host 127.0.0.1 --port 8000) &

echo "[2/5] Launching AI Engine (Port 8001)..."
(cd "$ROOT_DIR/saksham-aiml" && uvicorn ai_engine.main:app --host 127.0.0.1 --port 8001) &

echo "[3/5] Launching Route Analysis Service (Port 8002)..."
(cd "$ROOT_DIR/aibin-backend" && uvicorn route_analysis.main:app --host 127.0.0.1 --port 8002) &

echo "[4/5] Launching Alert Service (Port 8003)..."
(cd "$ROOT_DIR/aibin-backend" && uvicorn alert_service.main:app --host 127.0.0.1 --port 8003) &

echo "Waiting for internal microservices to warm up..."
sleep 3

echo "[5/5] Launching API Gateway on Render public port $PORT..."
cd "$ROOT_DIR/aibin-backend"
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
