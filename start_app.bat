@echo off
echo Starting Cruise Tracking Web App...

:: Start backend (Flask server)
start cmd /k "cd /d E:\Cruise Tracking Web App\backend && python server.py"

:: Start frontend (React app)
start cmd /k "cd /d E:\Cruise Tracking Web App\frontend && npm start"

echo All services started. You can now open http://localhost:3000
pause
