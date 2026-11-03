@echo off
rem En vivos del profesor del curso (El Trader Rolo): transcripcion + operativa con Claude Code (plan Pro) + publicacion.
rem Programado de lunes a viernes a las 11:30 y 12:00 (sesion de Nueva York) y 21:40 y 22:00 (sesion de Asia), hora de
rem Bogota (decision de Eduardo, 2026-11-02). Si YouTube aun no genero los subtitulos, ese directo queda para la siguiente.
cd /d "%~dp0.."
set PYTHONIOENCODING=utf-8
"C:\Users\franc\OneDrive\Desktop\Proyectos Python\Trading\.venv\Scripts\python.exe" local\rolo_vivos.py >> "%TEMP%\bolsa_radar_rolo.log" 2>&1
