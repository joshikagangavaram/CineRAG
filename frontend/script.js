const API_URL = "http://127.0.0.1:8000";

const messages = document.querySelector("#messages");
const form = document.querySelector("#chat-form");
const input = document.querySelector("#question");
const statusBadge = document.querySelector("#status");
const suggestionButtons = document.querySelectorAll("[data-question]");

function setStatus(text, className) {
  statusBadge.textContent = text;
  statusBadge.className = `status ${className || ""}`.trim();
}

function addMessage(role, text, sources = []) {
  const article = document.createElement("article");
  article.className = `message ${role}`;

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;

  if (sources.length > 0) {
    const sourceWrap = document.createElement("div");
    sourceWrap.className = "sources";

    sources.forEach((source) => {
      const item = document.createElement("div");
      item.className = "source";

      const title = document.createElement("strong");
      title.textContent = `${source.title} (${source.category})`;

      const body = document.createElement("span");
      body.textContent = source.text;

      item.append(title, body);
      sourceWrap.appendChild(item);
    });

    bubble.appendChild(sourceWrap);
  }

  article.appendChild(bubble);
  messages.appendChild(article);
  messages.scrollTop = messages.scrollHeight;
}

async function checkBackend() {
  try {
    const response = await fetch(`${API_URL}/health`);
    if (!response.ok) throw new Error("Backend unavailable");
    setStatus("Backend ready", "ready");
  } catch (error) {
    setStatus("Start backend: python backend/app.py", "error");
  }
}

async function ask(question) {
  addMessage("user", question);
  input.value = "";
  form.querySelector("button").disabled = true;

  try {
    const response = await fetch(`${API_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });

    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || "Request failed");

    addMessage("bot", payload.answer, payload.sources);
  } catch (error) {
    addMessage("bot", "I could not reach the RAG backend. Start it with: python backend/app.py");
    setStatus("Backend offline", "error");
  } finally {
    form.querySelector("button").disabled = false;
    input.focus();
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const question = input.value.trim();
  if (question) ask(question);
});

suggestionButtons.forEach((button) => {
  button.addEventListener("click", () => ask(button.dataset.question));
});

checkBackend();
