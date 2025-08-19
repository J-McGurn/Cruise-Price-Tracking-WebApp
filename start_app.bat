@echo off
echo Starting Cruise Tracking Web App...

:: Get the folder of this batch file
SET BASEDIR=%~dp0

:: Start backend (Flask server)
start cmd /k "cd /d "%BASEDIR%backend" && python server.py"

:: Start frontend (React app)
start cmd /k "cd /d "%BASEDIR%frontend" && npm start"

echo All services started. You can now open http://localhost:3000
pause
