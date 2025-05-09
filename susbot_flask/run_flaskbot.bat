@echo off
cd /d %~dp0

call .venv\Scripts\activate.bat
pip install -r requirements.txt

python -m flask_susbot.app
pause
