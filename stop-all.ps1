# TrafficVision AI — Stop All Services Script (Windows PowerShell)

Write-Host "Stopping all TrafficVision AI processes on ports 3000, 8000, 8001, 8002, 8003, 8080..." -ForegroundColor Yellow

$ports = @(3000, 8000, 8001, 8002, 8003, 8080)
foreach ($port in $ports) {
    try {
        $connections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
        if ($connections) {
            foreach ($conn in $connections) {
                $pidToKill = $conn.OwningProcess
                if ($pidToKill -and $pidToKill -ne 0) {
                    Write-Host "Terminating process PID $pidToKill listening on port $port..." -ForegroundColor Cyan
                    Stop-Process -Id $pidToKill -Force -ErrorAction SilentlyContinue
                }
            }
        }
    } catch {
        # continue
    }
}

Write-Host "All TrafficVision services stopped." -ForegroundColor Green
