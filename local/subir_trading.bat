@echo off
rem Sube a GitHub lo que los scripts de Bolsa-Radar generan DENTRO del repo Trading (bitacora viva y fuentes: tesis,
rem operativa e info de cada video; las transcripciones completas las ignora el .gitignore de Trading).
rem Lo llaman al final cava_diario.bat, lectura_ia_pc.bat, rolo_vivos.bat y publicar_desde_pc.bat (19-nov-2026: la Agenda
rem avisaba "Trading: cambios sin commit" porque nadie los subia). Solo toca esas dos carpetas.
setlocal
set "TD=%TRADING_DIR%"
if "%TD%"=="" set "TD=%USERPROFILE%\Proyectos\Trading"
cd /d "%TD%" || exit /b 0
git pull --rebase --autostash -q >> "%TEMP%\bolsa_radar_subir_trading.log" 2>&1
git add -- cerebro/4_bitacora_viva fuentes >> "%TEMP%\bolsa_radar_subir_trading.log" 2>&1
git diff --cached --quiet && exit /b 0
git commit -q -m "Bitacora viva y fuentes generadas por Bolsa-Radar (automatico)" >> "%TEMP%\bolsa_radar_subir_trading.log" 2>&1
git push -q >> "%TEMP%\bolsa_radar_subir_trading.log" 2>&1
exit /b 0
