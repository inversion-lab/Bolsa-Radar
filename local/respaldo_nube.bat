@echo off
cd /d "%~dp0.."
set "TRADING_DIR=C:\Users\franc\OneDrive\Desktop\Proyectos Python\Trading"
if not exist "%TRADING_DIR%\.venv\Scripts\python.exe" set "TRADING_DIR=%USERPROFILE%\Proyectos\Trading"
set PYTHONIOENCODING=utf-8
"%TRADING_DIR%\.venv\Scripts\python.exe" local\respaldo_nube.py >> "%TEMP%\bolsa_radar_respaldo.log" 2>&1
