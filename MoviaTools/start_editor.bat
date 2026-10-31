@echo off
cd /d "%~dp0"
python -c "import PyQt6" 2>nul || (
  echo Installerer PyQt6 ...
  python -m pip install PyQt6
)
python movia_editor_app.py
if errorlevel 1 pause
