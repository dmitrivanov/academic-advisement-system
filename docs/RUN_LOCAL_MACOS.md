# Run the Academic Advisement System Locally on macOS

These instructions begin with downloading the private GitHub repository and end with opening the application locally.

## Prerequisites

Install:

- [Git](https://git-scm.com/download/mac)
- Python 3.10 or newer
- A current web browser
- Access to the private GitHub repository

Open **Terminal** and confirm that Git and Python are available:

```bash
git --version
python3 --version
```

## 1. Download the repository

In Terminal, run:

```bash
git clone https://github.com/dmitrivanov/academic-advisement-system.git
cd academic-advisement-system
```

Because the repository is private, GitHub may ask you to authenticate. If prompted, sign in through GitHub or use a GitHub personal access token instead of an account password.

## 2. Create a virtual environment

```bash
python3 -m venv venv
```

## 3. Activate the virtual environment

```bash
source venv/bin/activate
```

The Terminal prompt will normally begin with `(venv)` after activation.

## 4. Install the dependencies

```bash
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

## 5. Configure local accounts

Run these commands in the same Terminal window:

```bash
export SESSION_SECRET="local-development-secret"
export APP_USERNAME="admin"
export APP_PASSWORD="admin"
export TESTER_USERNAME="tester"
export TESTER_PASSWORD="tester"
```

The application has two roles:

- Administrator: `admin` / `admin`
- Student tester: `tester` / `tester`

The tester can use student advising features but cannot open administrator pages or administrator APIs.

These are demonstration credentials. Use different passwords for a public or long-running deployment.

### Optional: enable AI features

Manual advising features work without an AI key. To enable the Gemini-based advisor, add:

```bash
export GEMINI_API_KEY="your-Gemini-key"
```

Never commit passwords, API keys, `.env` files, or production database URLs.

## 6. Create and seed the database

```bash
python3 seed_database.py
```

This creates or refreshes `advisor.db` from the curriculum CSV files under `docs/`.

## 7. Start the application

```bash
python3 -m uvicorn faq_fallback_api:app --reload --port 8000
```

Keep this Terminal window open while using the application.

## 8. Open the application

Open the following address in a browser:

<http://127.0.0.1:8000>

Sign in with either the administrator or tester account listed above.

## 9. Stop the application

Return to Terminal and press `Control+C`.

## Restart the application later

```bash
cd academic-advisement-system
source venv/bin/activate
python3 -m uvicorn faq_fallback_api:app --reload --port 8000
```

## Troubleshooting

### `No module named ...`

Activate the virtual environment and reinstall dependencies:

```bash
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

### Port 8000 is already in use

Use a different port:

```bash
python3 -m uvicorn faq_fallback_api:app --reload --port 8001
```

Then open <http://127.0.0.1:8001>.

### Programs do not appear

Rerun the database seed and restart the server:

```bash
python3 seed_database.py
```

### AI advisor reports that no API key is configured

Manual degree-progress, planning, and transfer features remain available. Set `GEMINI_API_KEY` and restart the server only if AI features are required.
