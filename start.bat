@echo off
call .\.venv\scripts\activate.bat
pip install -r requirements.txt
py ./manhwaviewer.py
