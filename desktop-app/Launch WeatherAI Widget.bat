@echo off
title WeatherAI Widget Launcher
echo.
echo  ====================================
echo     WeatherAI Desktop Widget
echo     Floating Chatbot for Windows
echo  ====================================
echo.
echo  [1] Starting the Python backend server...
start "" /B cmd /c "cd /d "%~dp0.." && python -m uvicorn main:app --host 127.0.0.1 --port 8000 > nul 2>&1"
timeout /t 3 /nobreak > nul

echo  [2] Launching WeatherAI Widget...
start "" "%~dp0dist\win-unpacked\WeatherAI Widget.exe"

echo.
echo  Done! Look for the  tornado icon in your taskbar / bottom-right of screen.
echo  Click it to open the weather chatbot.
echo.
echo  Press any key to close this launcher...
pause > nul
