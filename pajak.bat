@echo off
echo --- START ---

set PROJEKT_DIR=%~dp0

cd /d "%PROJEKT_DIR%zaliczenie"

"%PROJEKT_DIR%.venv\Scripts\python.exe" -m scrapy crawl ryanair

echo --- KONIEC ---
pause
