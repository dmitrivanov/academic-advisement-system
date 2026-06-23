#!/bin/bash

set -e

PROJECT_DIR="${1:-$(pwd)}"
MODULE_DIR="$PROJECT_DIR/frontend/reusable_ai_advisor"
CONFIG_DIR="$PROJECT_DIR/config"
LOGS_DIR="$PROJECT_DIR/logs"

printf "\nReusable AI Advisor Installer\n"
printf "Project directory: %s\n\n" "$PROJECT_DIR"

mkdir -p "$MODULE_DIR"
mkdir -p "$CONFIG_DIR"
mkdir -p "$LOGS_DIR"

# Copy files if installer is run from a package folder containing reusable_ai_advisor/
if [ -d "./reusable_ai_advisor" ]; then
  cp -R ./reusable_ai_advisor/* "$MODULE_DIR/"
  printf "Copied reusable_ai_advisor files to %s\n" "$MODULE_DIR"
else
  printf "WARNING: ./reusable_ai_advisor folder not found.\n"
  printf "Create/copy these files manually:\n"
  printf "  %s/ai_advisor_widget.js\n" "$MODULE_DIR"
  printf "  %s/ai_advisor_widget.css\n" "$MODULE_DIR"
fi

# Create default settings if not present
if [ ! -f "$CONFIG_DIR/ai_settings.json" ]; then
  cat > "$CONFIG_DIR/ai_settings.json" <<'JSON'
{
  "agent_id": "default_agent",
  "page_name": "Example Page",
  "page_url": "/example",
  "model": "gemini-2.5-flash",
  "system_prompt": "You are a helpful AI assistant. Use only the provided page context. If the context is insufficient, say what information is missing.",
  "logging_enabled": true,
  "show_metrics": true
}
JSON
  printf "Created default config: %s/ai_settings.json\n" "$CONFIG_DIR"
else
  printf "Config already exists: %s/ai_settings.json\n" "$CONFIG_DIR"
fi

# Create log file if not present
if [ ! -f "$LOGS_DIR/ai_advisor_logs.jsonl" ]; then
  touch "$LOGS_DIR/ai_advisor_logs.jsonl"
  printf "Created log file: %s/ai_advisor_logs.jsonl\n" "$LOGS_DIR"
else
  printf "Log file already exists: %s/ai_advisor_logs.jsonl\n" "$LOGS_DIR"
fi

printf "\nAdd this snippet to your HTML page:\n\n"
cat <<'HTML'
<link rel="stylesheet" href="/frontend/reusable_ai_advisor/ai_advisor_widget.css">
<script src="/frontend/reusable_ai_advisor/ai_advisor_widget.js"></script>

<button id="askAdvisorBtn">Ask AI Advisor</button>

<script>
function buildPageContext() {
  return {
    page_name: document.title,
    visible_text: document.body.innerText.slice(0, 5000)
  };
}

initAIAdvisorWidget({
  agentId: "default_agent",
  buttonSelector: "#askAdvisorBtn",
  endpoint: "/ai-agent-ask",
  pageName: document.title,
  contextProvider: buildPageContext
});
</script>
HTML

printf "\nBackend requirements:\n"
printf "  pip install fastapi uvicorn google-genai python-multipart itsdangerous pydantic\n"
printf "  export GEMINI_API_KEY=\"YOUR_REAL_GEMINI_KEY\"\n"
printf "  Add /ai-agent-ask endpoint to your FastAPI app.\n\n"

printf "Installation scaffold complete.\n"
