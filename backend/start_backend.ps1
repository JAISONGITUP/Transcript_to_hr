# Kill any existing processes on port 8000
Write-Host "Checking for existing processes on port 8000..." -ForegroundColor Yellow
$processes = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique

if ($processes) {
    Write-Host "Found $($processes.Count) process(es) on port 8000. Terminating..." -ForegroundColor Yellow
    foreach ($pid in $processes) {
        try {
            Stop-Process -Id $pid -Force -ErrorAction Stop
            Write-Host "Killed process $pid" -ForegroundColor Green
        } catch {
            Write-Host "Could not kill process $pid" -ForegroundColor Red
        }
    }
    Start-Sleep -Seconds 2
} else {
    Write-Host "Port 8000 is free" -ForegroundColor Green
}

# Activate virtual environment and start uvicorn with timeout
Write-Host "`nStarting backend server with 10-minute timeout..." -ForegroundColor Cyan
& .\venv\Scripts\Activate.ps1
uvicorn app:app --reload --timeout-keep-alive 600 --host 127.0.0.1 --port 8000
