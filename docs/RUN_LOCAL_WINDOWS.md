# Run the Academic Advisement System Locally on Windows

These instructions use **Windows PowerShell** and begin with downloading the private GitHub repository.

## Prerequisites

Install:

- [Git for Windows](https://git-scm.com/download/win)
- Python 3.10 or newer
- A current web browser
- Access to the private GitHub repository

During Python installation, select **Add Python to PATH**.

Open **PowerShell** and confirm that Git and Python are available:

```powershell
git --version
python --version
```

## 1. Download the repository

In PowerShell, run:

```powershell
git clone https://github.com/dmitrivanov/academic-advisement-system.git
cd academic-advisement-system
```

Because the repository is private, GitHub may ask you to authenticate. Sign in through GitHub or use a GitHub personal access token instead of an account password.

### Download ZIP alternative

If Git is unavailable:

1. Open the repository on GitHub.
2. Select **Code** and then **Download ZIP**.
3. Extract the ZIP file.
4. Open the extracted `academic-advisement-system` folder in PowerShell.
5. Continue with the next step.

## 2. Create a virtual environment

```powershell
python -m venv venv
```

## 3. Activate the virtual environment

```powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell reports that script execution is disabled, run the following commands in the same window:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

This policy change applies only to the current PowerShell process.

## 4. Install the dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 5. Configure local accounts

Run these commands in the same PowerShell window:

```powershell
$env:SESSION_SECRET="local-development-secret"
$env:APP_USERNAME="admin"
$env:APP_PASSWORD="admin"
$env:TESTER_USERNAME="tester"
$env:TESTER_PASSWORD="tester"
```

The application has two roles:

- Administrator: `admin` / `admin`
- Student tester: `tester` / `tester`

The tester can use student advising features but cannot open administrator pages or administrator APIs.

These are demonstration credentials. Use different passwords for a public or long-running deployment.

### Optional: enable AI features

Manual advising features work without an AI key. To enable the Gemini-based advisor, add:

```powershell
$env:GEMINI_API_KEY="your-Gemini-key"
```

Never commit passwords, API keys, `.env` files, or production database URLs.

## 6. Create and seed the database

```powershell
python seed_database.py
```

This creates or refreshes `advisor.db` from the curriculum CSV files under `docs/`.

## 7. Start the application

```powershell
python -m uvicorn faq_fallback_api:app --reload --port 8000
```

Keep this PowerShell window open while using the application.

## 8. Open the application

Open the following address in a browser:

<http://127.0.0.1:8000>

Sign in with either the administrator or tester account listed above.

## 9. Stop the application

Return to PowerShell and press `Control+C`.

## Restart the application later

```powershell
cd academic-advisement-system
.\venv\Scripts\Activate.ps1
python -m uvicorn faq_fallback_api:app --reload --port 8000
```

## Troubleshooting

### `python` is not recognized

Reinstall Python and select **Add Python to PATH**. On some Windows installations, the Python launcher can be used instead:

```powershell
py --version
```

If `py` works, replace `python` with `py` in the commands above.

### Running scripts is disabled

Use the process-scoped command from Step 3:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### Port 8000 is already in use

Start the application on another port:

```powershell
python -m uvicorn faq_fallback_api:app --reload --port 8001
```

Then open <http://127.0.0.1:8001>.

### Programs do not appear

Rerun the database seed and restart the server:

```powershell
python seed_database.py
```

### AI advisor reports that no API key is configured

Manual degree-progress, planning, and transfer features remain available. Set `GEMINI_API_KEY` and restart the server only if AI features are required.
