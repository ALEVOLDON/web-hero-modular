@echo off
cd /d "%~dp0"
echo Starting Modular Genesis 3D Hero on http://localhost:8765...
start http://localhost:8765/
python -m http.server 8765 --directory "web"
