@echo off
echo Starting Energy Monitoring Dashboard...

start "FastAPI Backend" cmd /k "cd /d "D:\Python Projects\Prediction model (Real Data)\backend" && uvicorn main:app --reload"

timeout /t 3 /nobreak > nul

start "React Frontend" cmd /k "cd /d "D:\Python Projects\Prediction model (Real Data)\frontend" && npm run dev"

echo Both servers starting...
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173

