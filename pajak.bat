@echo off
echo --- START ---

REM 1. Ustawienie terminala w glownym folderze
cd /d "%~dp0"

echo 2. Aktywuje srodowisko...
call .venv\Scripts\activate.bat

echo 3. Wchodze do folderu Scrapy...
cd zaliczenie

echo 4. Uruchamiam pajaka...
scrapy crawl ryanair

echo 5. Uruchamiam sortowanie...
python zaliczenie\sortowanie.py

echo --- GOTOWE ---
pause