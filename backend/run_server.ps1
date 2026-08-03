Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host "Starting SmartSnakebite FastAPI Backend" -ForegroundColor Cyan
Write-Host "=========================================================" -ForegroundColor Cyan

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

if (Test-Path "$scriptDir\venv\Scripts\python.exe") {
    Write-Host "[INFO] Using virtual environment: venv\Scripts\python.exe" -ForegroundColor Green
    & "$scriptDir\venv\Scripts\python.exe" -m uvicorn main:app --reload --port 8000
} else {
    Write-Warning "venv\Scripts\python.exe not found! Falling back to global uvicorn..."
    uvicorn main:app --reload --port 8000
}
