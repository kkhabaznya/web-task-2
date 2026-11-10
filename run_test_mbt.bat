@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PYTHONPATH=%CD%\src

coverage run -m pytest tests/test_mbt.py -v
coverage report -m --include="src\app.py"
coverage html --include="src\app.py"

pause