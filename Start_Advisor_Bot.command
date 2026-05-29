#!/bin/bash

# Academic Advisor Bot Launcher (Gemini Version)

PROJECT_DIR="$HOME/Downloads/advisor_bot"

echo "======================================"
echo " Academic Advisor Bot Launcher"
echo " Gemini Hybrid Version"
echo "======================================"
echo ""

if [ ! -d "$PROJECT_DIR" ]; then
  echo "ERROR: Project folder not found:"
  echo "$PROJECT_DIR"
  read -p "Press Enter to close..."
  exit 1
fi

cd "$PROJECT_DIR" || exit 1

echo "Project folder:"
pwd
echo ""

# Activate virtual environment
if [ ! -d "$PROJECT_DIR/venv" ]; then
  echo "ERROR: venv not found."
  echo "Create it first with:"
  echo "python3 -m venv venv"
  read -p "Press Enter to close..."
  exit 1
fi

echo "Activating virtual environment..."
source venv/bin/activate

# Check Gemini API key
if [ -z "$GEMINI_API_KEY" ]; then
  echo ""
  echo "ERROR: GEMINI_API_KEY is not set."
  echo ""
  echo "Run:"
  echo 'export GEMINI_API_KEY="YOUR_KEY"'
  echo ""
  read -p "Press Enter to close..."
  exit 1
fi

# Generate graph data
echo ""
echo "Generating graph data from CSV..."
python3 generate_graph_data.py

echo ""
echo "Starting Gemini fallback backend..."

osascript -e 'tell application "Terminal" to do script "cd '"$PROJECT_DIR"' && source venv/bin/activate && export GEMINI_API_KEY=\"'"$GEMINI_API_KEY"'\" && python3 -m uvicorn faq_fallback_api:app --reload --port 8001"'

sleep 3

echo "Starting frontend server..."

osascript -e 'tell application "Terminal" to do script "cd '"$PROJECT_DIR"' && python3 -m http.server 5500"'

sleep 2

echo "Opening browser..."

open "http://127.0.0.1:5500/frontend/faq_chat_hybrid.html"

echo ""
echo "System started successfully."
echo ""

read -p "Press Enter to close launcher..."