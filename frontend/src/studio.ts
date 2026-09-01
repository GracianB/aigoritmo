import { analyzeImage, fetchAvatars, speak, streamChat, type Avatar } from "./api";

type StudioState = {
  avatar: Avatar | null;
  roster: Avatar[];
  conversationId: string | null;
  muted: boolean;
  busy: boolean;
  selectedImage: File | null;
};

type PromptChip = { label: string; text: string; draw?: boolean };

const DEMO_AVATARS = ["arcana", "arcano"] as const;
const CLIP_GAP_MS = 850;
const WIZARD_CLIP = "/media/videos/wizard.mp4?v=1";

type PresenceState = "idle" | "thinking" | "writing" | "speaking";
type PresenceClip = { src: string; loops: number; id: "wizard" | "avatar" };

const STARTERS: PromptChip[] = [
  { label: "Lanza la tirada", text: "Sí, lanza una tirada de tres cartas sobre lo que más me inquieta ahora.", draw: true },
  { label: "Amor", text: "Quiero una lectura sobre el amor y lo que se está moviendo en mis vínculos.", draw: true },
  { label: "Trabajo", text: "Necesito claridad sobre mi camino laboral ahora mismo.", draw: true },
  { label: "Este mes", text: "¿Qué energía me acompaña este mes?", draw: true },
];

const FOLLOWUPS: PromptChip[] = [
  { label: "Profundiza", text: "Profundiza en la carta del presente y dime qué me pide hoy." },
  { label: "Consejo", text: "Dame un consejo concreto y practicable, sin misticismo vacío." },
  { label: "Sombra", text: "¿Qué me está frenando o qué no quiero ver?" },
  { label: "Otra tirada", text: "Haz otra tirada de tres cartas sobre este mismo tema.", draw: true },
];

const state: StudioState = {
  avatar: null,
  roster: [],
  conversationId: null,
  muted: false,
  busy: false,
  selectedImage: null,
};

const audioQueue: HTMLAudioElement[] = [];
let playing: HTMLAudioElement | null = null;
let lastSpoken = "";
let welcomePending = false;

export async function mountStudio(root: HTMLElement): Promise<void> {
  root.innerHTML = gateHtml();
  root.querySelector("#enter")?.addEventListener("click", () => void enter(root));
}

async function enter(root: HTMLElement): Promise<void> {
  try {
    const roster = await fetchAvatars();
    state.roster = roster.filter((item) => DEMO_AVATARS.includes(item.id as (typeof DEMO_AVATARS)[number]));
    state.avatar = state.roster.find((item) => item.id === "arcana") ?? state.roster[0] ?? null;
  } catch {
    root.innerHTML = errorGate("No puedo conectar con el backend. Arranca FastAPI en el puerto configurado.");
    return;
  }
  if (!state.avatar) {
    root.innerHTML = errorGate("Arcana no existe en el catálogo de avatares.");
    return;
  }
  welcomePending = true;
  renderStudio(root);
}

function orbMarkup(): string {
  return `<div class="orb" aria-hidden="true"><span class="orb__aura"></span><span class="orb__mist"></span><span class="orb__plasma"></span><span class="orb__swirl"></span><span class="orb__glass"></span><span class="orb__core"></span><span class="orb__ring"></span><span class="orb__shine"></span><span class="orb__rim"></span></div>`;
}

function clipsFor(avatar: Avatar): PresenceClip[] {
  const clips: PresenceClip[] = [];
  if (avatar.id === "arcana") clips.push({ src: WIZARD_CLIP, loops: 1, id: "wizard" });
  if (avatar.video) {
    const loops = 1;
    clips.push({ src: avatar.video, loops, id: "avatar" });
  }
  return clips;
}

function renderStudio(root: HTMLElement): void {
  const avatar = state.avatar!;
  const clips = clipsFor(avatar);
  const media = clips.length
    ? `<video class="presence__video" muted playsinline poster="${avatar.poster}"></video>`
    : "";

  root.innerHTML = `
    <main class="arcana" data-state="idle">
      <div class="stage">
        <div class="presence ${clips.length ? "" : "is-orb"}" data-state="idle">
          ${media}
          <div class="presence__orb">${orbMarkup()}</div>
          <p class="presence__caption" id="presence-caption">en espera</p>
        </div>
      </div>

      <header class="arcana__header">
        <div class="brand"><span class="brand__sigil">✦</span><span>Aigoritmo / ${avatar.name}</span></div>
        <div class="status">
          <div class="avatar-switch" id="avatar-switch">
            ${state.roster.map((item) => `<button type="button" data-avatar="${item.id}" class="${item.id === avatar.id ? "is-active" : ""}">${item.name}</button>`).join("")}
          </div>
          <span class="status__dot"></span><span id="voice-status">en espera</span>
        </div>
      </header>

      <section class="arcana__intro">
        <p class="eyebrow">AVATAR EXPERIMENTAL · 01</p>
        <h1>${avatar.name}</h1>
        <p>${avatar.description}</p>
        <div class="capabilities">
          <span>conversación</span><span>tarot</span><span>visión</span><span>voz</span>
        </div>
      </section>

      <section class="console">
        <div class="console__head">
          <div>
            <strong>Consulta</strong>
            <span id="feature">${avatar.feature}</span>
          </div>
          <div class="console__head-actions">
            <button class="icon-btn" id="mute" type="button" title="Activar o silenciar voz">◉ Voz</button>
            <button class="icon-btn" id="replay" type="button" title="Repetir última frase">↺ Oír</button>
            <button class="icon-btn" id="reset" type="button" title="Nueva conversación">↻ Nueva</button>
          </div>
        </div>

        <div class="quick-actions">
          <button class="ritual-btn" id="draw" type="button"><span>✦</span><b>Lanzar tirada</b><small>ella genera las tres cartas</small></button>
          <button class="ritual-btn" id="vision" type="button"><span>◈</span><b>Opcional: tu foto</b><small>solo si quieres que mire algo tuyo</small></button>
          <input id="image-input" type="file" accept="image/jpeg,image/png,image/webp" hidden />
        </div>

        <div class="image-preview" id="image-preview" hidden>
          <img id="preview-img" alt="Imagen seleccionada" />
          <div><strong>Imagen preparada</strong><span id="preview-name"></span></div>
          <button class="icon-btn" id="remove-image" type="button">Quitar</button>
        </div>

        <div class="transcript" id="transcript" aria-live="polite"></div>

        <div class="thinking" id="thinking" hidden><span></span><span></span><span></span><em>${avatar.name} interpreta…</em></div>

        <div class="suggestions" id="suggestions"></div>

        <form class="composer" id="composer">
          <textarea id="input" rows="1" maxlength="8000" placeholder="Dile qué te inquieta o pide una tirada. No hace falta enviar fotos."></textarea>
          <button class="mic" id="mic" type="button" title="Hablar" aria-label="Dictar">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5.5 11a6.5 6.5 0 0 0 13 0"/><path d="M12 17.5V21"/></svg>
          </button>
          <button class="send" id="send" type="submit" title="Enviar" aria-label="Enviar">
            <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M3.4 20.6 21 12 3.4 3.4l.1 6.7L15 12 3.5 13.9z"/></svg>
          </button>
        </form>
        <p class="disclaimer">El tarot es simbólico. La tirada la genera Arcana: no tienes que subir cartas. Voz local Piper.</p>
      </section>
    </main>
  `;

  const transcript = root.querySelector("#transcript") as HTMLElement;
  addBubble(transcript, "bot", avatar.welcome);
  renderSuggestions(root, STARTERS);
  bindStudio(root);
  bindPresence(root);
  if (!avatar.video) setPresence("idle");
}

function bindStudio(root: HTMLElement): void {
  root.querySelector("#avatar-switch")?.addEventListener("click", (event) => {
    const button = (event.target as HTMLElement).closest("button[data-avatar]") as HTMLButtonElement | null;
    if (!button || state.busy) return;
    const next = state.roster.find((item) => item.id === button.dataset.avatar);
    if (!next || next.id === state.avatar?.id) return;
    state.avatar = next;
    state.conversationId = null;
    welcomePending = true;
    clearImage(root);
    stopAudio();
    renderStudio(root);
  });
  root.querySelector("#mute")?.addEventListener("click", (event) => {
    state.muted = !state.muted;
    (event.currentTarget as HTMLButtonElement).textContent = state.muted ? "○ Voz" : "◉ Voz";
    if (state.muted) stopAudio();
  });
  root.querySelector("#replay")?.addEventListener("click", () => {
    if (lastSpoken) void speakLine(lastSpoken);
  });
  root.querySelector("#reset")?.addEventListener("click", () => resetConversation(root));
  root.querySelector("#draw")?.addEventListener("click", () => void drawCards(root));
  root.querySelector("#vision")?.addEventListener("click", () => (root.querySelector("#image-input") as HTMLInputElement).click());
  root.querySelector("#image-input")?.addEventListener("change", (event) => selectImage(root, event));
  root.querySelector("#remove-image")?.addEventListener("click", () => clearImage(root));
  root.querySelector("#composer")?.addEventListener("submit", (event) => {
    event.preventDefault();
    void send(root);
  });
  const input = root.querySelector("#input") as HTMLTextAreaElement;
  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      void send(root);
    }
  });
  root.querySelector("#suggestions")?.addEventListener("click", (event) => {
    const button = (event.target as HTMLElement).closest("button[data-prompt]") as HTMLButtonElement | null;
    if (!button || state.busy) return;
    const text = button.dataset.prompt ?? "";
    const draw = button.dataset.draw === "1";
    if (!text) return;
    (root.querySelector("#input") as HTMLTextAreaElement).value = text;
    if (draw) void drawCards(root);
    else void send(root);
  });
  bindMic(root);
}

function bindPresence(root: HTMLElement): void {
  const video = root.querySelector(".presence__video") as HTMLVideoElement | null;
  const clips = state.avatar ? clipsFor(state.avatar) : [];
  if (!video || !clips.length) {
    revealOrb(root);
    maybeWelcome();
    return;
  }
  let index = 0;
  let loops = 0;
  let gapTimer = 0;
  const stillActive = () => !root.querySelector(".presence")?.classList.contains("is-orb");
  const afterGap = (fn: () => void) => {
    window.clearTimeout(gapTimer);
    video.classList.add("is-holding");
    gapTimer = window.setTimeout(() => {
      video.classList.remove("is-holding");
      if (stillActive()) fn();
    }, CLIP_GAP_MS);
  };
  const startClip = (i: number) => {
    if (i >= clips.length) {
      revealOrb(root);
      maybeWelcome();
      return;
    }
    loops = 0;
    index = i;
    const clip = clips[i];
    video.src = clip.src;
    void video.play().catch(() => startClip(i + 1));
    if (clip.id === "avatar") maybeWelcome();
  };
  video.loop = false;
  video.addEventListener("ended", () => {
    if (!stillActive()) return;
    loops += 1;
    const clip = clips[index];
    if (clip && loops < clip.loops) {
      afterGap(() => {
        video.currentTime = 0;
        void video.play().catch(() => startClip(index + 1));
      });
      return;
    }
    afterGap(() => startClip(index + 1));
  });
  startClip(0);
  window.setTimeout(() => {
    revealOrb(root);
    maybeWelcome();
  }, 40000);
}

function maybeWelcome(): void {
  if (!welcomePending || !state.avatar) return;
  welcomePending = false;
  void speakLine(state.avatar.welcome);
}

function revealOrb(root: HTMLElement): void {
  const presence = root.querySelector(".presence");
  if (!presence || presence.classList.contains("is-orb")) return;
  presence.classList.add("is-orb");
  const video = presence.querySelector("video") as HTMLVideoElement | null;
  if (!video) return;
  window.setTimeout(() => {
    video.pause();
    video.removeAttribute("src");
    video.load();
  }, 950);
}

function bindMic(root: HTMLElement): void {
  const button = root.querySelector("#mic") as HTMLButtonElement | null;
  if (!button) return;
  const SpeechRecognition = (window as unknown as {
    SpeechRecognition?: new () => BrowserSpeech;
    webkitSpeechRecognition?: new () => BrowserSpeech;
  }).SpeechRecognition ?? (window as unknown as { webkitSpeechRecognition?: new () => BrowserSpeech }).webkitSpeechRecognition;
  if (!SpeechRecognition) {
    button.hidden = true;
    return;
  }
  const rec = new SpeechRecognition();
  rec.lang = "es-ES";
  rec.interimResults = true;
  rec.continuous = false;
  let live = false;
  button.addEventListener("click", () => {
    if (state.busy) return;
    if (live) {
      rec.stop();
      return;
    }
    try {
      rec.start();
    } catch {
      /* already started */
    }
  });
  rec.onstart = () => {
    live = true;
    button.classList.add("is-live");
    button.title = "Escuchando…";
  };
  rec.onend = () => {
    live = false;
    button.classList.remove("is-live");
    button.title = "Hablar";
  };
  rec.onerror = () => {
    live = false;
    button.classList.remove("is-live");
  };
  rec.onresult = (event) => {
    const input = root.querySelector("#input") as HTMLTextAreaElement;
    const chunks: string[] = [];
    for (let i = 0; i < event.results.length; i += 1) {
      chunks.push(event.results[i][0].transcript);
    }
    input.value = chunks.join(" ").trim();
    const last = event.results[event.results.length - 1];
    if (last?.isFinal && input.value) void send(root);
  };
}

function renderSuggestions(root: HTMLElement, chips: PromptChip[]): void {
  const wrap = root.querySelector("#suggestions");
  if (!wrap) return;
  wrap.innerHTML = chips
    .map((chip) => `<button type="button" data-prompt="${escapeHtml(chip.text)}" data-draw="${chip.draw ? "1" : "0"}">${escapeHtml(chip.label)}</button>`)
    .join("");
}

function resetConversation(root: HTMLElement): void {
  if (state.busy || !state.avatar) return;
  state.conversationId = null;
  clearImage(root);
  stopAudio();
  const transcript = root.querySelector("#transcript") as HTMLElement;
  transcript.replaceChildren();
  addBubble(transcript, "bot", state.avatar.welcome);
  renderSuggestions(root, STARTERS);
  (root.querySelector("#input") as HTMLTextAreaElement).focus();
  welcomePending = false;
  void speakLine(state.avatar.welcome);
}

function selectImage(root: HTMLElement, event: Event): void {
  const input = event.currentTarget as HTMLInputElement;
  const file = input.files?.[0] ?? null;
  if (!file) return;
  state.selectedImage = file;
  const preview = root.querySelector("#image-preview") as HTMLElement;
  const img = root.querySelector("#preview-img") as HTMLImageElement;
  const name = root.querySelector("#preview-name") as HTMLElement;
  img.src = URL.createObjectURL(file);
  name.textContent = `${file.name} · ${(file.size / 1024 / 1024).toFixed(1)} MB`;
  preview.hidden = false;
  (root.querySelector("#input") as HTMLTextAreaElement).placeholder = `¿Qué quieres que ${state.avatar?.name ?? "el avatar"} observe en esta imagen?`;
}

function clearImage(root: HTMLElement): void {
  state.selectedImage = null;
  const input = root.querySelector("#image-input") as HTMLInputElement | null;
  if (input) input.value = "";
  const preview = root.querySelector("#image-preview") as HTMLElement | null;
  if (preview) preview.hidden = true;
  const text = root.querySelector("#input") as HTMLTextAreaElement | null;
  if (text) text.placeholder = "Dile qué te inquieta o pide una tirada. No hace falta enviar fotos.";
}

async function drawCards(root: HTMLElement): Promise<void> {
  if (state.busy || !state.avatar) return;
  const input = root.querySelector("#input") as HTMLTextAreaElement;
  const question = input.value.trim() || "Haz una nueva tirada de tres cartas para el tema que estamos explorando.";
  input.value = "";
  await runChat(root, question, true);
}

async function send(root: HTMLElement): Promise<void> {
  if (state.busy || !state.avatar) return;
  const input = root.querySelector("#input") as HTMLTextAreaElement;
  const text = input.value.trim();
  if (!text && !state.selectedImage) return;
  input.value = "";

  if (state.selectedImage) {
    await runVision(root, text || "Interpreta esta imagen en el contexto de nuestra conversación.");
    return;
  }
  await runChat(root, text, wantsSpread(text));
}

function wantsSpread(text: string): boolean {
  const t = text.normalize("NFD").replace(/\p{Diacritic}/gu, "").toLowerCase().trim();
  if (/^(hola|holi|buenas|buen[oa]s?\s+(dias|tardes|noches)|hey|hi|hello|que tal|ey)[!.?]*$/.test(t)) {
    return false;
  }
  if (/^(si|ok|vale|adelante|hazlo|dale|lanza|tira)[!.?]*$/.test(t)) return true;
  return /\b(tirada|tarot|tira(r|me)? las cartas|otra tirada|haz(me)? una (tirada|lectura)|lanza(me)? (una )?tirada)\b/.test(t);
}

async function runChat(root: HTMLElement, text: string, draw: boolean): Promise<void> {
  if (!state.avatar) return;
  const transcript = root.querySelector("#transcript") as HTMLElement;
  setBusy(root, true);
  addBubble(transcript, "user", draw ? `✦ ${text}` : text);
  const bot = addBubble(transcript, "bot", "");

  try {
    await streamChat(text, state.avatar.id, state.conversationId, {
      onMeta: (id) => { state.conversationId = id; },
      onToken: (token) => {
        bot.textContent = (bot.textContent ?? "") + token;
        transcript.scrollTop = transcript.scrollHeight;
        if (state.busy && !playing) setPresence("writing");
      },
      onAudio: (url) => enqueueAudio(url),
      onImage: (url, caption, cards) => addSpread(transcript, url, caption, cards),
      onError: (code, message) => addBubble(transcript, "error", explain(code, message)),
    }, undefined, draw);
  } catch {
    addBubble(transcript, "error", "No se pudo contactar con la API.");
  } finally {
    if (!bot.textContent?.trim()) bot.remove();
    else lastSpoken = bot.textContent;
    renderSuggestions(root, FOLLOWUPS);
    setBusy(root, false);
  }
}

async function runVision(root: HTMLElement, prompt: string): Promise<void> {
  if (!state.avatar || !state.selectedImage) return;
  const transcript = root.querySelector("#transcript") as HTMLElement;
  const file = state.selectedImage;
  const previewUrl = URL.createObjectURL(file);
  addUserImage(transcript, previewUrl, prompt);
  setBusy(root, true);
  clearImage(root);
  try {
    const result = await analyzeImage(file, state.avatar.id, state.conversationId, prompt);
    state.conversationId = result.conversation_id;
    addBubble(transcript, "bot", result.text);
    lastSpoken = result.text;
    void speakLine(result.text);
    renderSuggestions(root, FOLLOWUPS);
  } catch (error) {
    addBubble(transcript, "error", error instanceof Error ? error.message : "No se pudo analizar la imagen.");
  } finally {
    setBusy(root, false);
  }
}

function setBusy(root: HTMLElement, busy: boolean): void {
  state.busy = busy;
  (root.querySelector("#send") as HTMLButtonElement).disabled = busy;
  (root.querySelector("#draw") as HTMLButtonElement).disabled = busy;
  (root.querySelector("#vision") as HTMLButtonElement).disabled = busy;
  (root.querySelector("#mic") as HTMLButtonElement).disabled = busy;
  (root.querySelector("#thinking") as HTMLElement).hidden = !busy;
  const suggestions = root.querySelector("#suggestions") as HTMLElement | null;
  if (suggestions) suggestions.hidden = busy;
  if (busy) {
    revealOrb(root);
    setPresence("thinking");
  } else if (!playing) {
    setPresence("idle");
  }
  if (!busy) (root.querySelector("#input") as HTMLTextAreaElement).focus();
}

function addBubble(transcript: HTMLElement, role: "user" | "bot" | "error", text: string): HTMLElement {
  const el = document.createElement("article");
  el.className = `bubble bubble--${role}`;
  const label = document.createElement("span");
  label.className = "bubble__label";
  label.textContent = role === "bot" ? (state.avatar?.name.toUpperCase() ?? "AVATAR") : role === "user" ? "TÚ" : "SISTEMA";
  const content = document.createElement("div");
  content.className = "bubble__content";
  content.textContent = text;
  el.append(label, content);
  transcript.appendChild(el);
  transcript.scrollTop = transcript.scrollHeight;
  return content;
}

function addSpread(
  transcript: HTMLElement,
  url: string,
  caption: string,
  cards?: Array<{ position: string; name: string }>,
): void {
  const wrap = document.createElement("figure");
  wrap.className = "spread";
  const frame = document.createElement("div");
  frame.className = "spread__frame";
  const img = document.createElement("img");
  img.src = url;
  img.alt = caption || "Tirada de tarot";
  img.loading = "lazy";
  frame.append(img);
  wrap.append(frame);
  const fig = document.createElement("figcaption");
  fig.innerHTML = `<strong>${escapeHtml(caption || "Tirada")}</strong>`;
  if (cards?.length) {
    const list = document.createElement("div");
    list.className = "spread__cards";
    for (const card of cards) {
      const chip = document.createElement("span");
      chip.textContent = `${card.position}: ${card.name}`;
      list.append(chip);
    }
    fig.append(list);
  }
  wrap.append(fig);
  transcript.append(wrap);
  const pin = () => {
    wrap.scrollIntoView({ block: "nearest" });
    transcript.scrollTop = transcript.scrollHeight;
  };
  img.addEventListener("load", pin);
  pin();
}

function addUserImage(transcript: HTMLElement, url: string, prompt: string): void {
  const wrap = document.createElement("figure");
  wrap.className = "user-image";
  const img = document.createElement("img");
  img.src = url;
  img.alt = `Imagen enviada a ${state.avatar?.name ?? "el avatar"}`;
  const fig = document.createElement("figcaption");
  fig.textContent = prompt;
  wrap.append(img, fig);
  transcript.append(wrap);
  transcript.scrollTop = transcript.scrollHeight;
}

async function speakLine(text: string): Promise<void> {
  if (state.muted || !state.avatar || !text.trim()) return;
  lastSpoken = text;
  const url = await speak(state.avatar.id, text);
  if (url) enqueueAudio(url);
}

function enqueueAudio(url: string): void {
  if (state.muted) return;
  const audio = new Audio(url);
  audioQueue.push(audio);
  if (!playing) void playNext();
}

async function playNext(): Promise<void> {
  const next = audioQueue.shift();
  if (!next) {
    playing = null;
    setSpeaking(false);
    return;
  }
  playing = next;
  setSpeaking(true);
  try {
    await next.play();
    await new Promise<void>((resolve) => {
      next.onended = () => resolve();
      next.onerror = () => resolve();
    });
  } catch { /* autoplay may be blocked */ }
  await playNext();
}

function stopAudio(): void {
  audioQueue.length = 0;
  if (playing) { playing.pause(); playing = null; }
  setSpeaking(false);
}

function setSpeaking(on: boolean): void {
  document.querySelector(".presence")?.classList.toggle("is-speaking", on);
  if (on) {
    setPresence("speaking");
    return;
  }
  setPresence(state.busy ? "thinking" : "idle");
}

function setPresence(mode: PresenceState): void {
  const labels: Record<PresenceState, string> = {
    idle: "en espera",
    thinking: "interpretando",
    writing: "escribiendo",
    speaking: "hablando",
  };
  document.querySelectorAll(".presence, .arcana").forEach((el) => {
    (el as HTMLElement).dataset.state = mode;
  });
  const caption = document.querySelector("#presence-caption");
  if (caption) caption.textContent = labels[mode];
  const status = document.querySelector("#voice-status");
  if (status) status.textContent = labels[mode];
}

function explain(code: string, message: string): string {
  if (code === "ollama_unavailable") return "Ollama no responde. Arráncalo y comprueba el modelo conversacional.";
  if (code === "ollama_vision_unavailable") return "La visión local no está lista. Ejecuta: ollama pull llama3.2-vision:11b";
  if (code === "piper_unavailable") return `La voz no está lista. ${message}`;
  return message;
}

function escapeHtml(value: string): string {
  return value.replace(/[&<>'"]/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" })[char] ?? char);
}

function gateHtml(): string {
  return `<div class="gate"><div class="gate__veil"></div><div class="gate__copy"><div class="gate__orb">${orbMarkup()}</div><p class="gate__kicker">Consulta privada</p><h1>Arcana</h1><p class="gate__lede">Tarot, voz y visión en local. Una presencia, no un espectáculo.</p><button class="enter" id="enter" type="button">Entrar</button><small class="gate__note">Nada sale de tu máquina</small></div></div>`;
}

function errorGate(message: string): string {
  return `<div class="gate gate--error"><div class="gate__copy"><p class="gate__kicker">Sin conexión</p><h1>Arcana</h1><p class="gate__lede">${escapeHtml(message)}</p></div></div>`;
}

type BrowserSpeech = {
  lang: string;
  interimResults: boolean;
  continuous: boolean;
  start: () => void;
  stop: () => void;
  onstart: (() => void) | null;
  onend: (() => void) | null;
  onerror: (() => void) | null;
  onresult: ((event: { results: ArrayLike<{ 0: { transcript: string }; isFinal: boolean }> }) => void) | null;
};
