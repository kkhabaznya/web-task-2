@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PYTHONPATH=%CD%\src

py -m coverage run -m pytest tests/test_mbt.py -v
py -m coverage report -m --include="src\app.py"
py -m coverage html --include="src\app.py"

pause