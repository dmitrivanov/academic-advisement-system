@echo off
cd /d %~dp0
if not exist .venv py -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install -r requirements.txt
if not exist .env copy .env.example .env
python -m uvicorn app:app --reload --port 8010

