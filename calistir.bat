@echo off
chcp 65001 >nul
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 (
  echo Python bulunamadi. https://www.python.org/downloads/ adresinden kurun ^("Add Python to PATH" kutusunu isaretleyin^).
  pause
  exit /b 1
)
if not exist .venv (
  echo Ilk kurulum yapiliyor, birkac dakika surebilir...
  python -m venv .venv
)
call .venv\Scripts\activate.bat
pip install -q -r requirements.txt
streamlit run app.py
