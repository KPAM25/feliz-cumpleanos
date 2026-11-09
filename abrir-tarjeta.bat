@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Tarjeta de cumpleanos
python servir.py
echo.
echo El servidor se detuvo.
pause
