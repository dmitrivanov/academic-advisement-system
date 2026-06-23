# AI Advisor Module

This module adds a reusable right-side AI Advisor drawer to any web page. The widget lives on the frontend, but the AI request, API key, settings, and logs are handled by a backend server so the API key is not exposed in browser JavaScript.

## What the module includes

```text
frontend/reusable_ai_advisor/
├── ai_advisor_widget.js
├── ai_advisor_widget.css
└── README.md

backend / app files
├── /ai-agent-ask endpoint
├── /admin/ai-settings page
├── /api/admin/ai-settings endpoint
├── /api/admin/ai-embed-snippet endpoint
├── config/ai_settings.json
└── logs/ai_advisor_logs.jsonl
```

## Required architecture

The module has two parts:

1. **Frontend widget**
   - Displays the AI drawer.
   - Sends the user's question and current page context to the backend.
   - Shows response time and token metrics when available.

2. **Backend service**
   - Keeps the API key private.
   - Stores editable prompt/settings.
   - Sends requests to Gemini.
   - Saves logs and usage metrics.

Do not put the Gemini API key in frontend JavaScript.

---

## Quick installation in an existing FastAPI project

### 1. Copy frontend files

Copy the reusable advisor folder into your project:

```bash
cp -R frontend/reusable_ai_advisor /path/to/your/project/frontend/
```

Your project should then have:

```text
frontend/reusable_ai_advisor/ai_advisor_widget.js
frontend/reusable_ai_advisor/ai_advisor_widget.css
```

### 2. Add the widget to a page

In any HTML page where you want the AI Advisor:

```html
<link rel="stylesheet" href="/frontend/reusable_ai_advisor/ai_advisor_widget.css">
<script src="/frontend/reusable_ai_advisor/ai_advisor_widget.js"></script>

<button id="askAdvisorBtn">Ask AI Advisor</button>
```

Then add a page-specific context function:

```html
<script>
function buildPageContext() {
  return {
    page_name: "Example Page",
    visible_text: document.body.innerText.slice(0, 5000)
  };
}

initAIAdvisorWidget({
  agentId: "example_agent",
  buttonSelector: "#askAdvisorBtn",
  endpoint: "/ai-agent-ask",
  pageName: "Example Page",
  contextProvider: buildPageContext
});
</script>
```

The context function is what makes the advisor useful. Each page should decide what information the AI should receive.

Examples:

```javascript
// Degree progress page
function buildPageContext() {
  return {
    program: CURRENT_REQUIREMENTS.program,
    completed_courses: [...COMPLETED_COURSES],
    recommendations: chooseRecommendedCourses()
  };
}
```

```javascript
// Simple generic page
function buildPageContext() {
  return {
    page_title: document.title,
    visible_text: document.body.innerText.slice(0, 5000)
  };
}
```

---

## Backend requirements

Install dependencies:

```bash
pip install fastapi uvicorn google-genai python-multipart itsdangerous pydantic
```

Set the API key on the server:

```bash
export GEMINI_API_KEY="YOUR_REAL_GEMINI_KEY"
```

Run the app:

```bash
python3 -m uvicorn app:app --reload --port 8001
```

The backend should expose:

```text
POST /ai-agent-ask
GET  /admin/ai-settings
GET  /api/admin/ai-settings
PUT  /api/admin/ai-settings
GET  /api/admin/ai-embed-snippet
```

---

## AI Settings page

Open:

```text
/admin/ai-settings
```

The settings page should allow editing:

- Agent ID
- Page name
- Page URL
- Model
- System prompt
- Logging enabled/disabled
- Metrics enabled/disabled

The API key should remain server-side. The settings page may display whether the key is configured, but should not expose the key to browser JavaScript.

Recommended storage:

```text
config/ai_settings.json
```

Example:

```json
{
  "agent_id": "advisor_progress",
  "page_name": "Degree Progress",
  "page_url": "/db-progress",
  "model": "gemini-2.5-flash",
  "system_prompt": "You are a helpful academic advisor. Use only the provided page context.",
  "logging_enabled": true,
  "show_metrics": true
}
```

---

## Logs

Advisor logs should be stored server-side:

```text
logs/ai_advisor_logs.jsonl
```

Each line can contain:

```json
{
  "timestamp": "2026-06-18T14:05:22Z",
  "agent_id": "advisor_progress",
  "ip": "127.0.0.1",
  "question": "What should I take next semester?",
  "answer": "...",
  "model": "gemini-2.5-flash",
  "usage": {
    "prompt_tokens": 123,
    "completion_tokens": 456,
    "total_tokens": 579,
    "response_time_ms": 1420
  }
}
```

---

## Generated embed snippet

A settings page can generate an embed snippet like this:

```html
<link rel="stylesheet" href="/frontend/reusable_ai_advisor/ai_advisor_widget.css">
<script src="/frontend/reusable_ai_advisor/ai_advisor_widget.js"></script>

<button id="advisorBtn">Ask AI Advisor</button>

<script>
initAIAdvisorWidget({
  agentId: "advisor_progress",
  buttonSelector: "#advisorBtn",
  endpoint: "/ai-agent-ask",
  pageName: "Degree Progress",
  contextProvider: buildAdvisorPageContext
});
</script>
```

The target page must define `buildAdvisorPageContext()`.

---

## Recommended project structure for reuse

```text
your_project/
├── app.py
├── config/
│   └── ai_settings.json
├── logs/
│   └── ai_advisor_logs.jsonl
├── frontend/
│   ├── reusable_ai_advisor/
│   │   ├── ai_advisor_widget.js
│   │   └── ai_advisor_widget.css
│   └── ai_settings.html
└── requirements.txt
```

---

## Security notes

- Never place the API key in frontend JavaScript.
- Keep `GEMINI_API_KEY` in environment variables or encrypted server-side storage.
- Log carefully. If the page context may include private student data, avoid logging full context.
- Add authentication before exposing `/admin/ai-settings` in production.

---

## Minimal reuse checklist

- [ ] Copy `ai_advisor_widget.js`
- [ ] Copy `ai_advisor_widget.css`
- [ ] Add the CSS and JS to target HTML page
- [ ] Add an advisor button
- [ ] Define `buildPageContext()`
- [ ] Add backend `/ai-agent-ask` endpoint
- [ ] Set `GEMINI_API_KEY` server-side
- [ ] Test advisor drawer
- [ ] Enable logs/metrics if needed

