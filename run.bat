@echo off
setlocal
echo =====================================================================
echo   CYBER-SNAKE BENCHMARK // JEV VS THE WORLD
echo   Repository: https://github.com/shreytalreja25/snake-game-benchmark
echo =====================================================================

cd /d "%~dp0"

set PYTHON_EXEC=..\openrouter_jev_dev\.venv\Scripts\python.exe

if not exist "%PYTHON_EXEC%" (
    set PYTHON_EXEC=python
)

echo [*] Launching FastAPI + WebSocket backend on http://localhost:8000 ...
"%PYTHON_EXEC%" -m uvicorn backend.server:app --host 0.0.0.0 --port 8000 --reload
pause
