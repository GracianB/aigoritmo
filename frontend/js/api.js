import { CONFIG } from "./config.js";

async function request(path, options = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), CONFIG.REQUEST_TIMEOUT_MS);
  try {
    const response = await fetch(`${CONFIG.API_BASE_URL}${path}`, {
      ...options,
      signal: controller.signal,
      headers: { "Accept": "application/json", ...(options.headers || {}) }
    });
    if (!response.ok) {
      let detail = `HTTP ${response.status}`;
      try { const data = await response.json(); detail = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail); } catch {}
      throw new Error(detail);
    }
    return response.json();
  } finally { clearTimeout(timeout); }
}

export const getHealth = () => request("/health");
export const getAvatarAssets = (personaId = CONFIG.DEFAULT_PERSONA) => request(`/api/avatar-assets/${encodeURIComponent(personaId)}`);

export async function sendChatMessage({ message, conversationId, personaId = CONFIG.DEFAULT_PERSONA }) {
  const payload = { message, persona_id: personaId };
  if (conversationId) payload.conversation_id = conversationId;
  return request("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json; charset=utf-8" },
    body: JSON.stringify(payload)
  });
}
