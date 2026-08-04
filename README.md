# Academic Advisement System

Academic Advisement System is a research prototype for exploring curriculum-aware
student advising. A student selects a CUNY campus and program, records completed
coursework, reviews degree progress, creates semester plans, and compares programs
for transfer or major-change analysis. Administrators can maintain curriculum data,
course equivalencies, and AI-advisor settings.

The deployed demonstration is available at
[academic-advisement-system.onrender.com](https://academic-advisement-system.onrender.com/).

## Main features

- Campus and academic-program selection
- New-student onboarding
- Interactive degree-progress graph
- Manual and AI-assisted semester planning
- Major-change and transfer analysis
- Administrator tools for programs and course equivalencies
- CSV-backed curriculum data in `docs/`

## Technology

- Python and FastAPI
- SQLAlchemy
- SQLite for local development and PostgreSQL on Render
- HTML, CSS, and JavaScript frontend
- Google Gemini for optional AI-advisor features

## Run locally

### 1. Prerequisites

Install:

- Git
- Python 3.10 or newer
- A current web browser

Confirm that Git and Python are available:

```bash
git --version
python3 --version
```

On Windows, `python` may be used instead of `python3`.

### 2. Clone the repository

Contributors should clone their own GitHub fork. Replace `YOUR_USERNAME` below:

```bash
git clone https://github.com/YOUR_USERNAME/academic-advisement-system.git
cd academic-advisement-system
git remote add upstream https://github.com/dmitrivanov/academic-advisement-system.git
git remote -v
```

Project maintainers may clone the upstream repository directly:

```bash
git clone https://github.com/dmitrivanov/academic-advisement-system.git
cd academic-advisement-system
```

### 3. Create and activate a virtual environment

macOS or Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

The terminal prompt normally shows `(venv)` after activation.

### 4. Install dependencies

```bash
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

On Windows, use `python` in place of `python3` if necessary.

### 5. Configure local environment variables

The application works without an AI key, but AI-advisor requests require a Google
Gemini API key. Environment variables can be exported in the current terminal.

macOS or Linux:

```bash
export SESSION_SECRET="local-development-secret"
export APP_USERNAME="admin"
export APP_PASSWORD="admin"
# Optional:
export GEMINI_API_KEY="your-key-here"
```

Windows PowerShell:

```powershell
$env:SESSION_SECRET="local-development-secret"
$env:APP_USERNAME="admin"
$env:APP_PASSWORD="admin"
# Optional:
$env:GEMINI_API_KEY="your-key-here"
```

Never commit API keys, passwords, `.env` files, or production database URLs.

### 6. Create and seed the local database

```bash
python3 seed_database.py
```

This creates `advisor.db` from the curriculum CSV files in `docs/`. The database is
ignored by Git and can be regenerated. Running the seed command refreshes program
data from the CSV files, so do not use it against a production database while doing
local development.

### 7. Start the application

Run the FastAPI application from the repository root:

```bash
python3 -m uvicorn faq_fallback_api:app --reload --port 8000
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) and sign in with the values from
`APP_USERNAME` and `APP_PASSWORD`. If those variables were not set, the local
development defaults are `admin` / `admin`.

The API health endpoint is available at
[http://127.0.0.1:8000/health](http://127.0.0.1:8000/health).

The FastAPI server serves both the API and frontend. A separate static-file server
is not required.

### 8. Stop and restart

Press `Ctrl+C` in the server terminal to stop it. After returning later:

```bash
cd academic-advisement-system
source venv/bin/activate
python3 -m uvicorn faq_fallback_api:app --reload --port 8000
```

Windows users should activate with `.\venv\Scripts\Activate.ps1`.

## Common problems

### `No module named ...`

Activate the virtual environment and reinstall dependencies:

```bash
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

### Port 8000 is already in use

Stop the other server or use another port:

```bash
python3 -m uvicorn faq_fallback_api:app --reload --port 8001
```

Then open `http://127.0.0.1:8001`.

### Programs do not appear

Make sure the seed command completed successfully:

```bash
python3 seed_database.py
```

Then restart the application.

### AI advisor says that the API key is not configured

This does not prevent manual degree-progress and transfer features from working.
Set `GEMINI_API_KEY` and restart the server to enable AI requests.

## Curriculum data

Program, course, pathway, institution, and equivalency seed data is stored in CSV
files under `docs/`. Treat curriculum changes as data changes: cite the official
source, keep the change limited to the requested program, reseed locally, and verify
the affected screens before opening a pull request.

## Contributing

Contributors must work from a fork and submit pull requests. Do not push directly to
the upstream `main` branch. See [CONTRIBUTING.md](CONTRIBUTING.md) for the complete
workflow and review checklist.

## Deployment

Render deploys the production application from the upstream `main` branch. Merging
a pull request can therefore trigger a production deployment. Only a maintainer
should merge after reviewing and testing the change.

## Prototype notice

This system supports research and demonstrations. It does not replace confirmation
from an official college catalog or a qualified academic advisor.
