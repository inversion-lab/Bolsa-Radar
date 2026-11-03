@echo off
rem En vivos del profesor del curso (El Trader Rolo): transcripcion + operativa con Claude Code (plan Pro) + publicacion.
rem Programado de lunes a viernes a las 12:15, 13:15 y 14:15 (sesion de Nueva York) y 22:30 y 23:30 (sesion de Asia),
rem hora de Bogota; YouTube tarda unas horas en generar los subtitulos del directo grabado.
cd /d "%~dp0.."
set PYTHONIOENCODING=utf-8
"C:\Users\franc\OneDrive\Desktop\Proyectos Python\Trading\.venv\Scripts\python.exe" local\rolo_vivos.py >> "%TEMP%\bolsa_radar_rolo.log" 2>&1
