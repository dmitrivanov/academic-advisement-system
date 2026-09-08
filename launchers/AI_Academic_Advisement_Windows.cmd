@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "REPOSITORY_URL=https://github.com/dmitrivanov/academic-advisement-system.git"
set "INSTALL_DIR=%USERPROFILE%\advising2_0"
set "APP_URL=http://127.0.0.1:8000"

where git >nul 2>nul
if errorlevel 1 (
  echo Git is missing. Install Git for Windows from https://git-scm.com/download/win
  pause
  exit /b 1
)

where py >nul 2>nul
if not errorlevel 1 (
  set "PYTHON_CMD=py -3"
) else (
  where python >nul 2>nul
  if errorlevel 1 (
    echo Python 3 is missing. Install it from https://www.python.org/downloads/windows/
    echo During installation, select Add Python to PATH.
    pause
    exit /b 1
  )
  set "PYTHON_CMD=python"
)

echo AI Academic Advisement - local setup and launcher
echo Installation folder: %INSTALL_DIR%
echo.

if exist "%INSTALL_DIR%" if not exist "%INSTALL_DIR%\.git" (
  echo %INSTALL_DIR% already exists but is not this Git repository.
  echo Rename that folder, then run this launcher again.
  pause
  exit /b 1
)

if not exist "%INSTALL_DIR%\.git" (
  echo Downloading the application...
  git clone "%REPOSITORY_URL%" "%INSTALL_DIR%" || goto :failure
) else (
  echo Checking GitHub for updates...
  git -C "%INSTALL_DIR%" switch main || goto :failure
  git -C "%INSTALL_DIR%" pull --ff-only origin main || goto :failure
)

cd /d "%INSTALL_DIR%" || goto :failure

if not exist "venv\Scripts\python.exe" (
  echo Creating the private Python environment...
  %PYTHON_CMD% -m venv venv || goto :failure
)

echo Checking application dependencies...
"venv\Scripts\python.exe" -m pip install --disable-pip-version-check -q -r requirements.txt || goto :failure

if not exist ".env" (
  echo Creating local-only accounts and session settings...
  for /f "delims=" %%S in ('"venv\Scripts\python.exe" -c "import secrets; print(secrets.token_urlsafe(48))"') do set "SESSION_VALUE=%%S"
  >.env echo SESSION_SECRET=!SESSION_VALUE!
  >>.env echo APP_USERNAME=admin
  >>.env echo APP_PASSWORD=admin
  >>.env echo TESTER_USERNAME=tester
  >>.env echo TESTER_PASSWORD=tester
  echo Local admin: admin / admin
  echo Local tester: tester / tester
)

findstr /b "GEMINI_API_KEY=" .env >nul 2>nul
if errorlevel 1 (
  echo.
  set /p "GEMINI_VALUE=Optional Gemini API key (press Enter to skip): "
  if defined GEMINI_VALUE >>.env echo GEMINI_API_KEY=!GEMINI_VALUE!
)

for /f "delims=" %%H in ('git rev-parse HEAD') do set "CURRENT_COMMIT=%%H"
set "LAST_SEEDED="
if exist ".launcher-seeded-commit" set /p LAST_SEEDED=<.launcher-seeded-commit
if not "%CURRENT_COMMIT%"=="%LAST_SEEDED%" goto :seed
if not exist "advisor.db" goto :seed
goto :start

:seed
echo Refreshing curriculum data for this version...
"venv\Scripts\python.exe" seed_database.py || goto :failure
>.launcher-seeded-commit echo %CURRENT_COMMIT%

:start
echo.
echo Starting AI Academic Advisement at %APP_URL%
echo Keep this window open. Press Control+C here to stop the application.
start "" "%APP_URL%"
"venv\Scripts\python.exe" -m uvicorn faq_fallback_api:app --port 8000
goto :eof

:failure
echo.
echo Setup could not continue. Review the error above.
pause
exit /b 1
