
import { sendChatMessage } from "./api.js";
import { escapeHtml, timeNow, scrollToBottom } from "./ui.js";

export class ChatController {
  constructor({ avatar, speech, onMetrics }) {
    this.avatar = avatar;
    this.speech = speech;
    this.onMetrics = onMetrics;
    this.conversationId = null;
    this.busy = false;

    this.messages = document.querySelector("#messages");
    this.form = document.querySelector("#chatForm");
    this.input = document.querySelector("#messageInput");
    this.sendButton = document.querySelector("#sendButton");
    this.typing = document.querySelector("#typingIndicator");

    this.form.addEventListener("submit", (event) => {
      event.preventDefault();
      this.submit(this.input.value);
    });

    this.input.addEventListener("keydown", (event) => {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        this.submit(this.input.value);
      }
    });

    this.input.addEventListener("input", () => this.resizeInput());
  }

  resizeInput() {
    this.input.style.height = "auto";
    this.input.style.height = `${Math.min(this.input.scrollHeight, 140)}px`;
  }

  async submit(text) {
    const message = text.trim();
    if (!message || this.busy) return;

    this.busy = true;
    this.sendButton.disabled = true;
    this.appendMessage("user", message);
    this.input.value = "";
    this.resizeInput();
    this.typing.classList.remove("hidden");
    this.avatar.setState("thinking");

    const started = performance.now();

    try {
      const data = await sendChatMessage({
        message,
        conversationId: this.conversationId
      });

      this.conversationId = data.conversation_id;
      const latency = performance.now() - started;

      this.typing.classList.add("hidden");
      this.avatar.setState("talking");

      const response = data.response || "No he podido generar una respuesta.";
      this.appendMessage("assistant", response, true);

      this.speech.speak(response);
      this.onMetrics?.({ latency });

      setTimeout(() => this.avatar.setState("idle"), 650);
    } catch (error) {
      this.typing.classList.add("hidden");
      this.avatar.setState("error");
      this.appendMessage("assistant", `He encontrado un problema al conectar con el sistema: ${error.message}`);
      setTimeout(() => this.avatar.setState("idle"), 2500);
    } finally {
      this.busy = false;
      this.sendButton.disabled = false;
      this.input.focus();
    }
  }

  appendMessage(role, text, animate = false) {
    const row = document.createElement("div");
    row.className = `message-row ${role}`;

    const name = role === "assistant" ? "ARCANA" : "TÚ";
    const bubbleClass = role === "assistant" ? "assistant" : "user";

    row.innerHTML = `
      <div class="message-avatar">${role === "assistant" ? "A" : "T"}</div>
      <div class="message-content">
        <div class="message-meta"><strong>${name}</strong><time>${timeNow()}</time></div>
        <div class="message-bubble ${bubbleClass}">${animate ? "" : escapeHtml(text)}</div>
      </div>
    `;

    this.messages.appendChild(row);
    const bubble = row.querySelector(".message-bubble");

    if (animate) {
      this.typeText(bubble, text);
    } else {
      scrollToBottom(this.messages);
    }

    this.onMetrics?.({ incrementMessages: 1 });
  }

  async typeText(element, text) {
    const chunk = Math.max(2, Math.ceil(text.length / 180));
    for (let i = 0; i < text.length; i += chunk) {
      element.textContent += text.slice(i, i + chunk);
      scrollToBottom(this.messages);
      await new Promise(resolve => setTimeout(resolve, 7));
    }
    scrollToBottom(this.messages, true);
  }

  reset() {
    this.conversationId = null;
    this.messages.innerHTML = "";
    this.appendMessage("assistant",
      "Nueva conversación iniciada. Estoy aquí para explorar contigo aquello que deseas comprender.",
      false
    );
    this.avatar.setState("idle");
  }
}
