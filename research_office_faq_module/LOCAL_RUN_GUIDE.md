# BMCC Research Office FAQ Prototype - Local Run Guide

## What this prototype does

A student opens the chatbot without logging in, types a question or selects a suggested question, and receives an answer from the reviewed FAQ database. The response identifies whether it was an exact deterministic match or AI-assisted wording and includes an approved source link when available.

Research Office staff open `/admin`, enter the local admin password, then search, add, edit, hide, delete, or bulk-import FAQ records. Saved changes are available to the chatbot immediately.

## macOS setup

1. Open Terminal and change to `research_office_faq_module`.
2. Run `python3 -m venv .venv`.
3. Run `source .venv/bin/activate`.
4. Run `python -m pip install -r requirements.txt`.
5. Run `cp .env.example .env`.
6. Open `.env` and replace the default `ADMIN_PASSWORD`.
7. Optionally add `GEMINI_API_KEY`. The prototype works without it.
8. Run `python -m uvicorn app:app --reload --port 8010`.
9. Open `http://127.0.0.1:8010`.

Alternatively, double-click `start_mac.command` and allow Terminal to run it.

## Windows setup

1. Install Python 3.11 or newer and select Add Python to PATH.
2. Open PowerShell and change to `research_office_faq_module`.
3. Run `py -m venv .venv`.
4. Run `.\.venv\Scripts\Activate.ps1`.
5. If script execution is blocked, run `Set-ExecutionPolicy -Scope Process Bypass`, then activate again.
6. Run `python -m pip install -r requirements.txt`.
7. Run `Copy-Item .env.example .env`.
8. Edit `.env` and replace `ADMIN_PASSWORD`; optionally add `GEMINI_API_KEY`.
9. Run `python -m uvicorn app:app --reload --port 8010`.
10. Open `http://127.0.0.1:8010`.

Alternatively, double-click `start_windows.bat`.

## Reproducible demo

1. On the chatbot, select or type `How much does CRSP pay?`.
2. Confirm the answer shows the reviewed $5,000 total and semester split.
3. Ask `Can an international student apply to CSTEP?`.
4. Confirm the assistant distinguishes CSTEP from CRSP/BFF eligibility.
5. Ask an unrelated question such as `Where can I park?`.
6. Confirm the assistant says it has no reviewed answer instead of inventing one.
7. Open `/admin`, enter the password from `.env`, choose New FAQ, add a test question and answer, and save.
8. Return to the chatbot and ask the new question. The new answer should be available immediately.

## Knowledge management and AI behavior

SQLite stores the FAQ records in `data/research_faq.db`. The deterministic retriever ranks question text, category, and administrator-supplied keywords. With no Gemini key, the highest reviewed answer is returned verbatim. With a key, Gemini receives only the top retrieved FAQ evidence and is instructed not to add facts. The chatbot never performs open-web search during an answer.

For bulk updates, import UTF-8 CSV with required columns `category`, `question`, and `answer`; optional columns are `keywords` and `source_url`.

## Prototype boundaries

This is a demonstration, not a production policy system. Deadlines and program details can change. Before deployment, add BMCC staff single sign-on, approval/version history, audit logs, unanswered-question analytics, scheduled review dates, policy conflict tests, backups, and a controlled synchronization process for approved BMCC pages.

