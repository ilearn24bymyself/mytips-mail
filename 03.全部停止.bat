@echo off
chcp 65001 >nul
cd /d "%~dp0"
python stop_all.py
pause
