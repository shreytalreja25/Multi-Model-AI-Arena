@echo off
setlocal
echo =====================================================================
echo   CYBER-ARENA BENCHMARK: SNAKE & TETRIS // JEV VS THE WORLD
echo   Repository: https://github.com/shreytalreja25/snake-game-benchmark
echo =====================================================================

cd /d "%~dp0"

set PYTHON_EXEC=..\openrouter_jev_dev\.venv\Scripts\python.exe
if not exist "%PYTHON_EXEC%" (
    set PYTHON_EXEC=python
)

echo [*] Building latest React client if needed...
if not exist "frontend_dist\index.html" (
    cd client
    call npm run build
    cd ..
)

echo [*] Launching FastAPI + WebSocket backend with React UI on http://localhost:8000 ...
"%PYTHON_EXEC%" -m uvicorn backend.server:app --host 0.0.0.0 --port 8000 --reload
pause
