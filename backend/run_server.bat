@echo off
echo =========================================================
echo Starting SmartSnakebite FastAPI Backend
echo =========================================================
cd /d "%~dp0"
if exist "venv\Scripts\python.exe" (
    echo [INFO] Using virtual environment: venv\Scripts\python.exe
    venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000
) else (
    echo [WARNING] venv\Scripts\python.exe not found! Falling back to global python...
    python -m uvicorn main:app --reload --port 8000
)
