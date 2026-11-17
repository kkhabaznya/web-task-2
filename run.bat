@echo off
chcp 65001 >nul

cd /d "%~dp0src"

python app.py --seed-file "%~dp0data.json"

pause