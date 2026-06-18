(function(){
  function formatMarkdown(text) {
    const safe = String(text || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");

    return safe
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      .replace(/\n\d+\.\s/g, match => `<br><strong>${match.trim()}</strong> `)
      .replace(/\n-\s/g, "<br>• ")
      .replace(/\n/g, "<br>");
  }

  function formatUsage(usage) {
    if (!usage) return "";
    const responseSeconds = usage.response_time_ms ? (usage.response_time_ms / 1000).toFixed(2) + "s" : "unavailable";
    const totalTokens = usage.total_tokens ?? "unavailable";
    const promptTokens = usage.prompt_tokens ?? "—";
    const completionTokens = usage.completion_tokens ?? "—";
    return `Response time: ${responseSeconds} · Tokens: ${totalTokens} · Prompt: ${promptTokens} · Reply: ${completionTokens}`;
  }

  function createWidget(config) {
    const state = {
      config: Object.assign({
        agentId: "advisor_progress",
        endpoint: "/ai-agent-ask",
        pageName: document.title,
        pageUrl: window.location.pathname,
        title: "AI Advisor",
        subtitle: "Ask questions using the current page context.",
        suggestedQuestions: [
          "What should I do next?",
          "Explain what is blocked or missing.",
          "Summarize this page for me."
        ],
        contextProvider: function(){
          return {
            page_title: document.title,
            page_url: window.location.pathname,
            visible_text: document.body.innerText.slice(0, 5000)
          };
        }
      }, config || {})
    };

    const backdrop = document.createElement("div");
    backdrop.className = "ai-advisor-backdrop ai-advisor-hidden";
    backdrop.onclick = close;

    const drawer = document.createElement("div");
    drawer.className = "ai-advisor-drawer";

    const suggestions = state.config.suggestedQuestions.map(q =>
      `<span class="ai-advisor-suggested-question" data-question="${q.replace(/"/g, '&quot;')}">${q}</span>`
    ).join("");

    drawer.innerHTML = `
      <div class="ai-advisor-header">
        <div>
          <h3>${state.config.title}</h3>
          <p>${state.config.subtitle}</p>
          <div class="ai-advisor-metrics-pill" data-role="metrics">No AI call yet</div>
        </div>
        <button class="ai-advisor-close" data-role="close">Close</button>
      </div>
      <div class="ai-advisor-body" data-role="messages">
        <div class="ai-advisor-message system">
          I can answer based on this page's current context.
          <div style="margin-top:8px;">${suggestions}</div>
        </div>
      </div>
      <div class="ai-advisor-input-area">
        <textarea data-role="question" placeholder="Ask a question about this page..."></textarea>
        <div class="ai-advisor-actions">
          <span class="ai-advisor-small-note">Uses current page context.</span>
          <button class="ai-advisor-send" data-role="send">Ask</button>
        </div>
      </div>
    `;

    document.body.appendChild(backdrop);
    document.body.appendChild(drawer);

    const messages = drawer.querySelector('[data-role="messages"]');
    const input = drawer.querySelector('[data-role="question"]');
    const sendButton = drawer.querySelector('[data-role="send"]');
    const metrics = drawer.querySelector('[data-role="metrics"]');

    drawer.querySelector('[data-role="close"]').onclick = close;
    sendButton.onclick = send;

    drawer.querySelectorAll('.ai-advisor-suggested-question').forEach(el => {
      el.onclick = () => { input.value = el.dataset.question; input.focus(); };
    });

    function open() {
      backdrop.classList.remove("ai-advisor-hidden");
      drawer.classList.add("open");
      setTimeout(() => input.focus(), 150);
    }

    function close() {
      drawer.classList.remove("open");
      backdrop.classList.add("ai-advisor-hidden");
    }

    function addMessage(role, text, usage) {
      const div = document.createElement("div");
      div.className = `ai-advisor-message ${role}`;
      div.innerHTML = `<div>${formatMarkdown(text)}</div>`;

      if (usage) {
        const meta = document.createElement("div");
        meta.className = "ai-advisor-message-meta";
        meta.textContent = formatUsage(usage);
        div.appendChild(meta);
        metrics.textContent = formatUsage(usage);
      }

      messages.appendChild(div);
      messages.scrollTop = messages.scrollHeight;
    }

    async function send() {
      const question = input.value.trim();
      if (!question) return;

      addMessage("user", question);
      input.value = "";
      sendButton.disabled = true;
      sendButton.textContent = "Thinking...";

      try {
        const pageContext = await state.config.contextProvider();
        const response = await fetch(state.config.endpoint, {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({
            agent_id: state.config.agentId,
            page_name: state.config.pageName,
            page_url: state.config.pageUrl,
            user_question: question,
            page_context: pageContext
          })
        });

        if (!response.ok) throw new Error(`AI request failed (${response.status})`);
        const data = await response.json();
        addMessage("assistant", data.answer || "No answer returned.", data.usage || null);
      } catch (err) {
        addMessage("assistant", `Error: ${err.message}`);
      } finally {
        sendButton.disabled = false;
        sendButton.textContent = "Ask";
      }
    }

    document.addEventListener("keydown", function(event) {
      if (event.key === "Escape") close();
      if ((event.metaKey || event.ctrlKey) && event.key === "Enter" && drawer.classList.contains("open")) send();
    });

    return { open, close, send };
  }

  window.initAIAdvisorWidget = function(config) {
    const widget = createWidget(config || {});
    const selector = config && (config.mountButtonSelector || config.buttonSelector);
    if (selector) {
      const button = document.querySelector(selector);
      if (button) button.onclick = widget.open;
    }
    return widget;
  };
})();
