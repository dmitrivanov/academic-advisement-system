#!/bin/bash

# Academic Advisor Bot Launcher for macOS
# Double-click this .command file to start the app.

PROJECT_DIR="$HOME/Downloads/advisor_bot"

echo "======================================"
echo " Academic Advisor Bot Launcher"
echo "======================================"
echo ""

if [ ! -d "$PROJECT_DIR" ]; then
  echo "ERROR: Project folder not found:"
  echo "$PROJECT_DIR"
  echo ""
  echo "Move advisor_bot to ~/Downloads/advisor_bot or edit PROJECT_DIR in this launcher."
  read -p "Press Enter to close..."
  exit 1
fi

cd "$PROJECT_DIR" || exit 1

echo "Project folder:"
pwd
echo ""

# Check Ollama
if command -v ollama >/dev/null 2>&1; then
  echo "Checking Ollama..."
  if curl -s http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
    echo "Ollama is already running."
  else
    echo "Starting Ollama in a new Terminal window..."
    osascript -e 'tell application "Terminal" to do script "ollama serve"'
    sleep 3
  fi
else
  echo "ERROR: Ollama is not installed."
  echo "Install it from https://ollama.com"
  read -p "Press Enter to close..."
  exit 1
fi

# Check venv
if [ ! -d "$PROJECT_DIR/venv" ]; then
  echo "Virtual environment not found. Creating venv..."
  python3 -m venv venv
fi

echo "Generating graph data from CSV..."
cd "$PROJECT_DIR"
source venv/bin/activate
python3 generate_graph_data.py

echo "Starting FastAPI fallback backend..."
osascript -e 'tell application "Terminal" to do script "cd '$PROJECT_DIR' && source venv/bin/activate && python3 -m uvicorn faq_fallback_api:app --reload --port 8001"'

sleep 2

echo "Starting frontend server..."
osascript -e 'tell application "Terminal" to do script "cd '$PROJECT_DIR' && python3 -m http.server 5500"'

sleep 2

echo "Opening browser..."
open "http://127.0.0.1:5500/frontend/faq_chat_hybrid.html"

echo ""
echo "Done."
echo "If the page does not open, use:"
echo "http://127.0.0.1:5500/frontend/faq_chat_hybrid.html"
echo ""
read -p "Press Enter to close this launcher window..."
