@echo off
echo --- START ---

cd /d "%~dp0"

call .venv\Scripts\activate.bat

cd zaliczenie

scrapy crawl ryanair

