# BMCC Research Office FAQ Prototype

An isolated local prototype for answering student questions about undergraduate research at BMCC. It was seeded from the Research Office planning document `Bot4BMCCResearchOffice` and deliberately does not depend on the Academic Advisement database.

## What is implemented

- Modern no-login student chat with typed questions and quick question chips.
- Fast deterministic retrieval over approved FAQ records.
- Optional Gemini wording assistance restricted to the retrieved FAQ evidence.
- Safe fallback when the knowledge base does not contain a reviewed answer.
- Source links attached to answers.
- Password-protected staff interface at `/admin`.
- Staff search, add, edit, enable/disable, delete, and CSV import.
- SQLite storage created automatically in `data/research_faq.db`.

The prototype does **not** browse the open web while answering. Official BMCC URLs are stored as citations. This keeps responses economical and follows the document requirement that AI not introduce random web information.

## Quick start

### macOS

```bash
cd research_office_faq_module
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
uvicorn app:app --reload --port 8010
```

Open <http://127.0.0.1:8010>. Staff FAQ manager: <http://127.0.0.1:8010/admin>.

### Windows PowerShell

```powershell
cd research_office_faq_module
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m uvicorn app:app --reload --port 8010
```

Edit `.env` and set a private `ADMIN_PASSWORD`. `GEMINI_API_KEY` is optional: without it, the chatbot still works using deterministic retrieval and exact reviewed answers.

## CSV import format

Required columns: `category`, `question`, `answer`. Optional columns: `keywords`, `source_url`.

```csv
category,question,answer,keywords,source_url
Applications,When is the deadline?,Check the current program page.,deadline;apply,https://www.bmcc.cuny.edu/...
```

## Recommended production follow-up

Add institutional sign-in for staff, audit/version history, approved-page synchronization, analytics for unanswered questions, human review states, automated tests for policy conflicts, and a production WSGI/ASGI deployment configuration.

