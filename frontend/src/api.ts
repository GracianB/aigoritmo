export type ChatHandlers = {
  onMeta?: (conversationId: string) => void;
  onToken?: (text: string) => void;
  onAudio?: (url: string) => void;
  onImage?: (url: string, caption: string, cards?: Array<{ position: string; name: string }>) => void;
  onError?: (code: string, message: string) => void;
  onDone?: () => void;
};

export async function streamChat(
  message: string,
  avatarId: string,
  conversationId: string | null,
  handlers: ChatHandlers,
  signal?: AbortSignal,
  drawCards = false,
): Promise<void> {
  const response = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      avatar_id: avatarId,
      conversation_id: conversationId,
      draw_cards: drawCards,
    }),
    signal,
  });
  if (!response.ok || !response.body) {
    handlers.onError?.("http_error", `El servidor respondió ${response.status}.`);
    return;
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const blocks = buffer.split("\n\n");
    buffer = blocks.pop() ?? "";
    for (const block of blocks) dispatchSse(block, handlers);
  }
  if (buffer.trim()) dispatchSse(buffer, handlers);
}

function dispatchSse(block: string, handlers: ChatHandlers): void {
  let event = "message";
  const dataLines: string[] = [];
  for (const line of block.split("\n")) {
    if (line.startsWith("event:")) event = line.slice(6).trim();
    else if (line.startsWith("data:")) dataLines.push(line.slice(5).trim());
  }
  if (!dataLines.length) return;
  let payload: Record<string, unknown> = {};
  try {
    payload = JSON.parse(dataLines.join("\n")) as Record<string, unknown>;
  } catch {
    return;
  }
  if (event === "meta" && typeof payload.conversation_id === "string") handlers.onMeta?.(payload.conversation_id);
  if (event === "token" && typeof payload.text === "string") handlers.onToken?.(payload.text);
  if (event === "audio" && typeof payload.url === "string") handlers.onAudio?.(payload.url);
  if (event === "image" && typeof payload.url === "string") {
    handlers.onImage?.(
      payload.url,
      typeof payload.caption === "string" ? payload.caption : "",
      Array.isArray(payload.cards) ? payload.cards as Array<{ position: string; name: string }> : undefined,
    );
  }
  if (event === "error") {
    handlers.onError?.(
      typeof payload.code === "string" ? payload.code : "error",
      typeof payload.message === "string" ? payload.message : "Error",
    );
  }
  if (event === "done") handlers.onDone?.();
}

export type Avatar = {
  id: string;
  name: string;
  description: string;
  video: string | null;
  poster: string;
  welcome: string;
  feature: string;
  capabilities: Record<string, boolean>;
};

export async function fetchAvatars(): Promise<Avatar[]> {
  const response = await fetch("/api/avatars");
  if (!response.ok) throw new Error("No se pudo cargar el roster");
  const body = (await response.json()) as { avatars: Avatar[] };
  return body.avatars;
}

export async function speak(avatarId: string, text: string): Promise<string | null> {
  const response = await fetch("/api/speak", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ avatar_id: avatarId, text }),
  });
  if (!response.ok) return null;
  const body = (await response.json()) as { url?: string };
  return typeof body.url === "string" ? body.url : null;
}

export type VisionResult = { conversation_id: string; text: string };

export async function analyzeImage(
  file: File,
  avatarId: string,
  conversationId: string | null,
  prompt: string,
): Promise<VisionResult> {
  const form = new FormData();
  form.append("image", file);
  form.append("avatar_id", avatarId);
  if (conversationId) form.append("conversation_id", conversationId);
  form.append("prompt", prompt);
  const response = await fetch("/api/vision/analyze", { method: "POST", body: form });
  const body = (await response.json()) as VisionResult & { code?: string; message?: string };
  if (!response.ok) throw new Error(body.message || `Error visual ${response.status}`);
  return body;
}
