
import { getHealth } from "./api.js";
import { AvatarController } from "./avatar.js";
import { ChatController } from "./chat.js";
import { SpeechController } from "./speech.js";

const avatar = new AvatarController();
const speech = new SpeechController();

const metrics = {
  messages: 0,
  startedAt: Date.now(),
  latency: null
};

function updateMetrics(change = {}) {
  if (change.incrementMessages) metrics.messages += change.incrementMessages;
  if (typeof change.latency === "number") metrics.latency = change.latency;

  document.querySelector("#metricMessages").textContent = metrics.messages;
  document.querySelector("#metricLatency").textContent =
    metrics.latency ? `${(metrics.latency / 1000).toFixed(1)}s` : "--";
}

setInterval(() => {
  const elapsed = Math.floor((Date.now() - metrics.startedAt) / 1000);
  const minutes = String(Math.floor(elapsed / 60)).padStart(2, "0");
  const seconds = String(elapsed % 60).padStart(2, "0");
  document.querySelector("#metricSession").textContent = `${minutes}:${seconds}`;
}, 1000);

const chat = new ChatController({
  avatar,
  speech,
  onMetrics: updateMetrics
});

async function checkHealth() {
  const dot = document.querySelector("#apiStatusDot");
  const text = document.querySelector("#apiStatusText");

  try {
    const health = await getHealth();
    dot.className = "status-dot";
    text.textContent = "API ONLINE";
    document.querySelector("#modelLabel").textContent = health.chat_model || "LOCAL AI";
    if (health.version) document.querySelector("#versionLabel").textContent = `v${health.version}`;
  } catch (error) {
    dot.className = "status-dot offline";
    text.textContent = "API OFFLINE";
    avatar.setState("error");
  }
}

document.querySelectorAll(".suggestion-card").forEach(button => {
  button.addEventListener("click", () => chat.submit(button.dataset.prompt));
});

document.querySelector("#newConversationBtn").addEventListener("click", () => {
  chat.reset();
  metrics.messages = 0;
  metrics.startedAt = Date.now();
  metrics.latency = null;
  updateMetrics();
  document.querySelector("#conversationTitle").textContent = "Nueva conversación";
});

document.querySelector("#soundToggle").addEventListener("click", (event) => {
  const enabled = speech.toggle();
  event.currentTarget.textContent = enabled ? "🔊" : "🔇";
  event.currentTarget.title = enabled ? "Desactivar voz" : "Activar voz";
});

checkHealth();
setInterval(checkHealth, 30000);
