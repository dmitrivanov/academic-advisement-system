# Run CUNY Beyond Locally on macOS

## Prerequisites

Install Git, Python 3.10 or newer, and a current web browser. You also need read access to the private GitHub repository.

Confirm the tools in Terminal:

```bash
git --version
python3 --version
```

## 1. Download the repository

```bash
git clone https://github.com/dmitrivanov/academic-advisement-system.git
cd academic-advisement-system
```

If GitHub requests authentication, sign in with GitHub or use a personal access token. GitHub account passwords do not work for Git command-line authentication.

## 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

The Terminal prompt normally begins with `(venv)`.

## 3. Install dependencies

```bash
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

## 4. Configure local accounts

```bash
export SESSION_SECRET="replace-this-for-any-shared-environment"
export APP_USERNAME="admin"
export APP_PASSWORD="admin"
export TESTER_USERNAME="tester"
export TESTER_PASSWORD="tester"
```

These demonstration credentials are for local testing. CUNY Beyond itself does not require login.

Optional AI functionality requires a Gemini key:

```bash
export GEMINI_API_KEY="your-Gemini-key"
```

Career matching, CPL preparation, degree requirements, and manual planning work without an AI key.

## 5. Create and seed the database

```bash
python3 seed_database.py
```

This creates or refreshes `advisor.db`, imports curricula, and loads reviewed CUNY Beyond careers and mappings.

## 6. Start the server

```bash
python3 -m uvicorn faq_fallback_api:app --reload --port 8000
```

Keep Terminal open. Uvicorn reports when the server is ready.

## 7. Open CUNY Beyond

Open `http://127.0.0.1:8000`. This is the primary no-login chatbot entry point. The direct `http://127.0.0.1:8000/cuny-beyond` address also works.

No login is required. For authenticated pages, open `http://127.0.0.1:8000/login` and use the local administrator or tester credentials.

## 8. Reproducible chatbot test

1. Select **High-school student** and send the answer.
2. Enter `Data Analyst` or select a career tag.
3. Choose **No** for current employment.
4. Select one to five skills.
5. Select **None of these** for prior learning.
6. Generate the reviewed program matches.
7. Confirm the conversation shows prior answers as user bubbles and the result includes official sources.

## Stop and restart

Press `Control+C` to stop. Later, restart with:

```bash
cd academic-advisement-system
source venv/bin/activate
python3 -m uvicorn faq_fallback_api:app --reload --port 8000
```

## Troubleshooting

- Missing module: activate `venv` and rerun `python3 -m pip install -r requirements.txt`.
- Empty programs or careers: rerun `python3 seed_database.py`, then restart.
- Port in use: replace `8000` with `8001` in the start command and browser address.
- Database locked: stop other local server or seed processes and retry.
- AI key missing: continue with deterministic features or configure `GEMINI_API_KEY` and restart.
