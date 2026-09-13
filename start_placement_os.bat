@echo off
title Placement OS Launcher
echo ===================================================
echo           Starting Placement OS Local Servers
echo ===================================================
echo.
echo Starting Django Backend Server (Port 8000)...
start "Placement OS - Django Backend" cmd /k "cd /d %~dp0 && .\venv\Scripts\activate && python manage.py runserver 8000"

echo Starting Next.js Frontend Server (Port 3000)...
start "Placement OS - Next.js Frontend" cmd /k "cd /d %~dp0placement-frontend && npm run dev"

echo Waiting for servers to initialize...
timeout /t 4 /nobreak >nul

echo Opening Placement OS in your default browser...
start http://localhost:3000

echo.
echo ===================================================
echo Placement OS is running!
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000
echo ===================================================
echo.
