@echo off
call .\.venv\scripts\activate.bat
auto-py-to-exe -c .\manhwaviewer-pyautoinst-config.json
