const API_URL = "/chat";
const SESSION_STORAGE_KEY = "atapia_session_id";
const CONVERSATIONS_STORAGE_KEY = "atapia_conversations";

const messagesEl = document.querySelector("#messages");
const formEl = document.querySelector("#chatForm");
const inputEl = document.querySelector("#messageInput");
const loadingEl = document.querySelector("#loading");
const errorEl = document.querySelector("#error");
const sessionIdEl = document.querySelector("#sessionId");
const chatTabEl = document.querySelector("#chatTab");
const historyTabEl = document.querySelector("#historyTab");
const chatViewEl = document.querySelector("#chatView");
const historyViewEl = document.querySelector("#historyView");
const historyListEl = document.querySelector("#historyList");
const newConversationButtonEl = document.querySelector("#newConversationButton");
const resetSessionButtonEl = document.querySelector("#resetSessionButton");
const demoCaseButtonEls = document.querySelectorAll("[data-demo-message]");

function getSessionId() {
  const existingSessionId = localStorage.getItem(SESSION_STORAGE_KEY);

  if (existingSessionId) {
    return existingSessionId;
  }

  const sessionId = crypto.randomUUID();
  localStorage.setItem(SESSION_STORAGE_KEY, sessionId);
  return sessionId;
}

let sessionId = getSessionId();
sessionIdEl.textContent = sessionId;

function getConversations() {
  const rawConversations = localStorage.getItem(CONVERSATIONS_STORAGE_KEY);

  if (!rawConversations) {
    return {};
  }

  try {
    return JSON.parse(rawConversations);
  } catch (error) {
    console.error(error);
    return {};
  }
}

function saveConversations(conversations) {
  localStorage.setItem(
    CONVERSATIONS_STORAGE_KEY,
    JSON.stringify(conversations),
  );
}

function getCurrentConversation() {
  const conversations = getConversations();

  if (!conversations[sessionId]) {
    conversations[sessionId] = {
      session_id: sessionId,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      messages: [],
    };
    saveConversations(conversations);
  }

  return conversations[sessionId];
}

function saveConversationMessage(role, content, metadata = null) {
  const conversations = getConversations();
  const conversation = conversations[sessionId] || {
    session_id: sessionId,
    created_at: new Date().toISOString(),
    messages: [],
  };

  conversation.messages.push({
    role,
    content,
    metadata,
    created_at: new Date().toISOString(),
  });
  conversation.updated_at = new Date().toISOString();
  conversations[sessionId] = conversation;
  saveConversations(conversations);
  renderHistory();
}

function setLoading(isLoading) {
  loadingEl.hidden = !isLoading;
  inputEl.disabled = isLoading;
  formEl.querySelector("button").disabled = isLoading;
  resetSessionButtonEl.disabled = isLoading;
  demoCaseButtonEls.forEach((buttonEl) => {
    buttonEl.disabled = isLoading;
  });
}

function setError(isVisible) {
  errorEl.hidden = !isVisible;
}

function setActiveView(viewName) {
  const isChat = viewName === "chat";

  chatTabEl.classList.toggle("active", isChat);
  historyTabEl.classList.toggle("active", !isChat);
  chatViewEl.classList.toggle("active", isChat);
  historyViewEl.classList.toggle("active", !isChat);

  if (!isChat) {
    renderHistory();
  }
}

function appendMessage(role, content, metadata = null) {
  const messageEl = document.createElement("article");
  messageEl.className = `message ${role}`;
  messageEl.textContent = content;

  if (metadata) {
    const hasSafetySignal =
      String(metadata.risk_level ?? "").toLowerCase() === "critical" ||
      metadata.safety_bypassed === true ||
      String(metadata.safety_bypassed).toLowerCase() === "true";

    if (hasSafetySignal) {
      messageEl.classList.add("safety-signal");
    }

    const metadataEl = document.createElement("div");
    metadataEl.className = "metadata";
    metadataEl.classList.toggle("safety-signal", hasSafetySignal);

    const titleEl = document.createElement("strong");
    titleEl.textContent = "Demo diagnostics";

    const listEl = document.createElement("dl");
    [
      ["Emotion", metadata.emotion ?? "unknown"],
      ["Risk level", metadata.risk_level ?? "unknown"],
      ["Safety bypass", metadata.safety_bypassed ?? false],
      ["Needs exploration", metadata.needs_exploration ?? false],
      ["Response time", metadata.response_time ?? "unknown"],
      ["Session ID", metadata.session_id ?? sessionId],
    ].forEach(([label, value]) => {
      const termEl = document.createElement("dt");
      const descriptionEl = document.createElement("dd");
      termEl.textContent = label;
      descriptionEl.textContent = String(value);
      listEl.append(termEl, descriptionEl);
    });

    metadataEl.append(titleEl, listEl);
    messageEl.appendChild(metadataEl);
  }

  messagesEl.appendChild(messageEl);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function renderCurrentConversation() {
  messagesEl.innerHTML = "";
  const conversation = getCurrentConversation();

  conversation.messages.forEach((message) => {
    appendMessage(message.role, message.content, message.metadata);
  });
}

function getConversationTitle(conversation) {
  const firstUserMessage = conversation.messages.find(
    (message) => message.role === "user",
  );

  if (!firstUserMessage) {
    return "New conversation";
  }

  if (firstUserMessage.content.length <= 64) {
    return firstUserMessage.content;
  }

  return `${firstUserMessage.content.slice(0, 61)}...`;
}

function renderHistory() {
  const conversations = Object.values(getConversations()).sort(
    (first, second) =>
      new Date(second.updated_at).getTime() -
      new Date(first.updated_at).getTime(),
  );

  historyListEl.innerHTML = "";

  if (conversations.length === 0) {
    const emptyEl = document.createElement("p");
    emptyEl.className = "empty-history";
    emptyEl.textContent = "No previous conversations yet.";
    historyListEl.appendChild(emptyEl);
    return;
  }

  conversations.forEach((conversation) => {
    const itemEl = document.createElement("article");
    itemEl.className = "history-item";

    const summaryEl = document.createElement("div");
    const titleEl = document.createElement("strong");
    const metaEl = document.createElement("span");
    titleEl.textContent = getConversationTitle(conversation);
    metaEl.textContent = `${conversation.messages.length} messages | ${conversation.session_id}`;
    summaryEl.append(titleEl, metaEl);

    const buttonEl = document.createElement("button");
    buttonEl.type = "button";
    buttonEl.textContent = "Open";
    buttonEl.addEventListener("click", () => {
      sessionId = conversation.session_id;
      localStorage.setItem(SESSION_STORAGE_KEY, sessionId);
      sessionIdEl.textContent = sessionId;
      renderCurrentConversation();
      setActiveView("chat");
      inputEl.focus();
    });

    itemEl.append(summaryEl, buttonEl);
    historyListEl.appendChild(itemEl);
  });
}

async function sendMessage(message) {
  const requestStart = performance.now();
  const response = await fetch(API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      session_id: sessionId,
      message,
    }),
  });

  if (!response.ok) {
    throw new Error(`API request failed with status ${response.status}`);
  }

  const data = await response.json();
  const measuredLatencySeconds = (performance.now() - requestStart) / 1000;

  return {
    ...data,
    response_time:
      typeof data.latency_seconds === "number"
        ? `${data.latency_seconds.toFixed(1)}s`
        : `${measuredLatencySeconds.toFixed(1)}s`,
  };
}

async function handleMessageSubmit(message) {
  if (!message) {
    return;
  }

  appendMessage("user", message);
  saveConversationMessage("user", message);
  inputEl.value = "";
  setError(false);
  setLoading(true);

  try {
    const data = await sendMessage(message);
    appendMessage("assistant", data.assistant_message || "", {
      emotion: data.emotion,
      risk_level: data.risk_level,
      safety_bypassed: data.safety_bypassed,
      needs_exploration: data.needs_exploration,
      response_time: data.response_time,
      session_id: sessionId,
    });
    saveConversationMessage("assistant", data.assistant_message || "", {
      emotion: data.emotion,
      risk_level: data.risk_level,
      safety_bypassed: data.safety_bypassed,
      needs_exploration: data.needs_exploration,
      response_time: data.response_time,
      session_id: sessionId,
    });
  } catch (error) {
    console.error(error);
    setError(true);
  } finally {
    setLoading(false);
    inputEl.focus();
  }
}

function startNewSession() {
  sessionId = crypto.randomUUID();
  localStorage.setItem(SESSION_STORAGE_KEY, sessionId);
  sessionIdEl.textContent = sessionId;
  messagesEl.innerHTML = "";
  inputEl.value = "";
  setError(false);
  getCurrentConversation();
  renderHistory();
  setActiveView("chat");
  inputEl.focus();
}

formEl.addEventListener("submit", async (event) => {
  event.preventDefault();
  await handleMessageSubmit(inputEl.value.trim());
});

chatTabEl.addEventListener("click", () => {
  setActiveView("chat");
});

historyTabEl.addEventListener("click", () => {
  setActiveView("history");
});

newConversationButtonEl.addEventListener("click", startNewSession);
resetSessionButtonEl.addEventListener("click", startNewSession);

demoCaseButtonEls.forEach((buttonEl) => {
  buttonEl.addEventListener("click", async () => {
    const message = buttonEl.dataset.demoMessage;
    inputEl.value = message;
    await handleMessageSubmit(message);
  });
});

getCurrentConversation();
renderCurrentConversation();
renderHistory();
