@echo off
title TrafficVision AI Stopper
echo Stopping all TrafficVision AI processes on ports 3000, 8000, 8001, 8002, 8003, 8080...

for %%P in (3000 8000 8001 8002 8003 8080) do (
    for /f "tokens=5" %%a in ('netstat -a -n -o ^| findstr :%%P ^| findstr LISTENING') do (
        echo Killing PID %%a on port %%P...
        taskkill /F /PID %%a >nul 2>&1
    )
)

echo All TrafficVision services stopped.
