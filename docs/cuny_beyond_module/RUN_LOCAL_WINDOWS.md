# Run CUNY Beyond Locally on Windows

These instructions use Windows PowerShell.

## Prerequisites

Install Git for Windows, Python 3.10 or newer, and a current browser. During Python installation, select **Add Python to PATH**. You need read access to the private repository.

```powershell
git --version
python --version
```

## 1. Download the repository

```powershell
git clone https://github.com/dmitrivanov/academic-advisement-system.git
cd academic-advisement-system
```

Alternatively, download the repository ZIP from GitHub, extract it, and open the extracted folder in PowerShell.

## 2. Create and activate a virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If script execution is blocked:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

This policy change lasts only for the current PowerShell window.

## 3. Install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 4. Configure local accounts

```powershell
$env:SESSION_SECRET="replace-this-for-any-shared-environment"
$env:APP_USERNAME="admin"
$env:APP_PASSWORD="admin"
$env:TESTER_USERNAME="tester"
$env:TESTER_PASSWORD="tester"
```

CUNY Beyond exploration does not require login. These demonstration accounts provide access to the linked authenticated application.

Optional AI functionality:

```powershell
$env:GEMINI_API_KEY="your-Gemini-key"
```

## 5. Create and seed the database

```powershell
python seed_database.py
```

## 6. Start the server

```powershell
python -m uvicorn faq_fallback_api:app --reload --port 8000
```

Keep PowerShell open while testing.

## 7. Open CUNY Beyond

Open `http://127.0.0.1:8000`. This is the primary no-login chatbot entry point. The direct `http://127.0.0.1:8000/cuny-beyond` address also works.

For authenticated pages, use `http://127.0.0.1:8000/login` with `admin` / `admin` or `tester` / `tester` unless you changed the environment variables.

## 8. Reproducible chatbot test

1. Select **High-school student**.
2. Enter `Registered Nurse` or choose it as a quick option.
3. Answer the employment question.
4. Select skills such as **Helping people** and **Communicating ideas**.
5. Select a prior-learning option or **None of these**.
6. Generate matches and confirm Nursing A.A.S. appears with official-source information.

## Stop and restart

Press `Control+C`. Later run:

```powershell
cd academic-advisement-system
.\venv\Scripts\Activate.ps1
python -m uvicorn faq_fallback_api:app --reload --port 8000
```

## Troubleshooting

- `python` not found: reinstall Python with PATH enabled or use `py` instead of `python`.
- Activation blocked: apply the process-scoped execution-policy command above.
- Missing module: activate the environment and reinstall `requirements.txt`.
- Empty data: rerun `python seed_database.py` and restart.
- Port in use: use port `8001` in both server command and browser address.
