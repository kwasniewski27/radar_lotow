@echo off

call "%~dp0.venv\Scripts\activate.bat"

cd "%~dp0zaliczenie"

scrapy crawl ryanair

python zaliczenie\sortowanie.py
