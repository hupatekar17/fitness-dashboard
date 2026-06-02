@echo off
REM Launch backend (FastAPI on :8000) and frontend (Vite on :5173) in new windows.
cd /d "%~dp0"

echo Starting backend on http://localhost:8000 ...
start "Dashboard Backend" cmd /k "cd backend && if exist .venv\Scripts\activate.bat call .venv\Scripts\activate.bat && uvicorn main:app --reload --port 8000"

timeout /t 3 /nobreak >nul

echo Starting frontend on http://localhost:5173 ...
start "Dashboard Frontend" cmd /k "cd frontend && npm run dev"

timeout /t 5 /nobreak >nul

echo.
echo Dashboard launching at http://localhost:5173
echo Backend health: http://localhost:8000/api/health
echo.
start http://localhost:5173
