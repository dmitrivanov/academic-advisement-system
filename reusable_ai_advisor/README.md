# Reusable AI Advisor Widget

This is a drop-in right-side AI advisor drawer for any page.

## Files

- `ai_advisor_widget.js`
- `ai_advisor_widget.css`

## Basic usage

```html
<link rel="stylesheet" href="/frontend/reusable_ai_advisor/ai_advisor_widget.css">
<script src="/frontend/reusable_ai_advisor/ai_advisor_widget.js"></script>

<button id="aiAdvisorButton">Ask AI Advisor</button>

<script>
initAIAdvisorWidget({
  agentId: "advisor_progress",
  mountButtonSelector: "#aiAdvisorButton",
  endpoint: "/ai-agent-ask",
  pageName: "Degree Progress",
  pageUrl: "/db-progress",
  contextProvider: function() {
    return buildAdvisorPageContext();
  }
});
</script>
```

## Important

Do not put API keys in frontend JavaScript. API keys must remain server-side.
