#!/bin/bash

set -euo pipefail

REPOSITORY_URL="https://github.com/dmitrivanov/academic-advisement-system.git"
INSTALL_DIR="$HOME/advising2_0"
APP_URL="http://127.0.0.1:8000"

finish_with_error() {
  echo
  echo "Setup could not continue."
  echo "$1"
  echo
  read -r -p "Press Return to close this window. " _
  exit 1
}

command -v git >/dev/null 2>&1 || finish_with_error "Git is missing. Install the Xcode Command Line Tools with: xcode-select --install"
command -v python3 >/dev/null 2>&1 || finish_with_error "Python 3 is missing. Install it from https://www.python.org/downloads/macos/"

echo "AI Academic Advisement - local setup and launcher"
echo "Installation folder: $INSTALL_DIR"
echo

if [ -e "$INSTALL_DIR" ] && [ ! -d "$INSTALL_DIR/.git" ]; then
  finish_with_error "$INSTALL_DIR already exists but is not this Git repository. Rename that folder, then run this launcher again."
fi

if [ ! -d "$INSTALL_DIR/.git" ]; then
  echo "Downloading the application..."
  git clone "$REPOSITORY_URL" "$INSTALL_DIR"
else
  echo "Checking GitHub for updates..."
  git -C "$INSTALL_DIR" switch main
  git -C "$INSTALL_DIR" pull --ff-only origin main
fi

cd "$INSTALL_DIR"

if [ ! -x "venv/bin/python3" ]; then
  echo "Creating the private Python environment..."
  python3 -m venv venv
fi

source venv/bin/activate
echo "Checking application dependencies..."
python3 -m pip install --disable-pip-version-check -q -r requirements.txt

if [ ! -f .env ]; then
  echo "Creating local-only accounts and session settings..."
  SESSION_VALUE="$(python3 -c 'import secrets; print(secrets.token_urlsafe(48))')"
  {
    echo "SESSION_SECRET=$SESSION_VALUE"
    echo "APP_USERNAME=admin"
    echo "APP_PASSWORD=admin"
    echo "TESTER_USERNAME=tester"
    echo "TESTER_PASSWORD=tester"
  } > .env
  chmod 600 .env
  echo "Local admin: admin / admin"
  echo "Local tester: tester / tester"
fi

if ! grep -q '^GEMINI_API_KEY=' .env; then
  echo
  read -r -s -p "Optional Gemini API key (press Return to skip): " GEMINI_VALUE
  echo
  if [ -n "$GEMINI_VALUE" ]; then
    printf 'GEMINI_API_KEY=%s\n' "$GEMINI_VALUE" >> .env
  fi
fi

CURRENT_COMMIT="$(git rev-parse HEAD)"
LAST_SEEDED=""
if [ -f .launcher-seeded-commit ]; then
  LAST_SEEDED="$(tr -d '\r\n' < .launcher-seeded-commit)"
fi
if [ "$CURRENT_COMMIT" != "$LAST_SEEDED" ] || [ ! -f advisor.db ]; then
  echo "Refreshing curriculum data for this version..."
  python3 seed_database.py
  printf '%s\n' "$CURRENT_COMMIT" > .launcher-seeded-commit
fi

echo
echo "Starting AI Academic Advisement at $APP_URL"
echo "Keep this window open. Press Control+C here to stop the application."

python3 -m uvicorn faq_fallback_api:app --port 8000 &
SERVER_PID=$!
trap 'kill "$SERVER_PID" 2>/dev/null || true' EXIT INT TERM
sleep 2
open "$APP_URL"
wait "$SERVER_PID"
