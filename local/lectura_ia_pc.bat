@echo off
rem Lectura con IA en el PC (Claude Code, plan Pro) mientras la API no tiene saldo. Programada a diario 8:10 Bogotá.
cd /d "%~dp0.."
set "TRADING_DIR=C:\Users\franc\OneDrive\Desktop\Proyectos Python\Trading"
if not exist "%TRADING_DIR%\.venv\Scripts\python.exe" set "TRADING_DIR=%USERPROFILE%\Proyectos\Trading"
set PYTHONIOENCODING=utf-8
"%TRADING_DIR%\.venv\Scripts\python.exe" local\lectura_ia_pc.py >> "%TEMP%\bolsa_radar_lectura.log" 2>&1
