import { analyzeImage, fetchAvatars, fetchHealth, speak, streamChat, type Avatar } from "./api";

type StudioState = {
  avatar: Avatar | null;
  roster: Avatar[];
  conversationId: string | null;
  muted: boolean;
  busy: boolean;
  selectedImage: File | null;
};

type PromptChip = { label: string; text: string; draw?: boolean };
type FailedTurn = { text: string; draw: boolean };

const DEMO_AVATARS = ["arcana", "arcano"] as const;
const CLIP_GAP_MS = 850;
const WIZARD_CLIP = "/media/videos/wizard.mp4?v=land";

type PresenceState = "idle" | "thinking" | "writing" | "speaking";
type PresenceClip = { src: string; loops: number; id: "wizard" | "avatar" };

const STARTERS: PromptChip[] = [
  { label: "Lanza la tirada", text: "Sí, lanza una tirada de una carta sobre lo que más me inquieta ahora.", draw: true },
  { label: "Amor", text: "Quiero una lectura de una carta sobre el amor y lo que se mueve en mis vínculos.", draw: true },
  { label: "Trabajo", text: "Tira una carta sobre mi camino laboral ahora mismo.", draw: true },
  { label: "Este mes", text: "¿Qué energía me acompaña este mes? Una carta basta.", draw: true },
];

const FOLLOWUPS: PromptChip[] = [
  { label: "Profundiza", text: "Profundiza en esta carta y dime qué me pide hoy." },
  { label: "Consejo", text: "Dame un consejo concreto y practicable, sin misticismo vacío." },
  { label: "Sombra", text: "¿Qué me está frenando o qué no quiero ver?" },
  { label: "Otra tirada", text: "Haz otra tirada de una carta sobre este mismo tema.", draw: true },
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
let lastFailed: FailedTurn | null = null;
let previewObjectUrl: string | null = null;
let presenceGen = 0;

export async function mountStudio(root: HTMLElement): Promise<void> {
  renderGate(root);
}

function renderGate(root: HTMLElement, error?: string): void {
  root.innerHTML = error ? errorGate(error) : gateHtml();
  const enterBtn = root.querySelector("#enter") as HTMLButtonElement | null;
  const retryBtn = root.querySelector("#retry") as HTMLButtonElement | null;
  enterBtn?.addEventListener("click", () => void enter(root));
  retryBtn?.addEventListener("click", () => void enter(root));
  bindGateMedia(root);
  (enterBtn ?? retryBtn)?.focus();
}

function bindGateMedia(root: HTMLElement): void {
  const video = root.querySelector(".gate__video") as HTMLVideoElement | null;
  if (!video) return;
  if (prefersReducedMotion()) {
    video.removeAttribute("autoplay");
    video.pause();
    video.classList.add("is-still");
    return;
  }
  video.addEventListener("error", () => video.classList.add("is-missing"));
}

async function enter(root: HTMLElement): Promise<void> {
  const action = root.querySelector("#enter, #retry") as HTMLButtonElement | null;
  if (action) {
    action.disabled = true;
    action.textContent = "Abriendo…";
  }
  try {
    const roster = await fetchAvatars();
    state.roster = roster.filter((item) => DEMO_AVATARS.includes(item.id as (typeof DEMO_AVATARS)[number]));
    state.avatar = state.roster.find((item) => item.id === "arcana") ?? state.roster[0] ?? null;
  } catch {
    renderGate(root, "backend");
    return;
  }
  if (!state.avatar) {
    renderGate(root, "avatar");
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
    clips.push({ src: avatar.video, loops: 1, id: "avatar" });
  }
  return clips;
}

function canSee(avatar: Avatar): boolean {
  return Boolean(avatar.capabilities.analyze_image);
}

function renderStudio(root: HTMLElement): void {
  const avatar = state.avatar!;
  const clips = clipsFor(avatar);
  const media = clips.length
    ? `<video class="presence__video" muted playsinline poster="${avatar.poster}" aria-hidden="true"></video>`
    : "";
  const vision = canSee(avatar);

  root.innerHTML = `
    <main class="arcana${clips.length ? "" : " is-orb"}" data-state="idle" data-avatar="${avatar.id}">
      <a class="skip" href="#input">Ir a la consulta</a>
      <div class="stage">
        <div class="presence ${clips.length ? "" : "is-orb"}" data-state="idle">
          ${media}
          <div class="presence__cluster">
            ${orbMarkup()}
            <p class="presence__caption" id="presence-caption">en espera</p>
          </div>
        </div>
      </div>

      <header class="arcana__header">
        <div class="brand"><span class="brand__sigil" aria-hidden="true">✦</span><span>Aigoritmo / ${escapeHtml(avatar.name)}</span></div>
        <div class="status">
          <div class="avatar-switch" id="avatar-switch" role="tablist" aria-label="Elegir presencia">
            ${state.roster.map((item) => `<button type="button" role="tab" data-avatar="${item.id}" aria-selected="${item.id === avatar.id}" class="${item.id === avatar.id ? "is-active" : ""}">${escapeHtml(item.name)}</button>`).join("")}
          </div>
          <span class="status__dot" aria-hidden="true"></span><span id="voice-status">en espera</span>
        </div>
      </header>

      <section class="console" aria-label="Consulta">
        <div class="console__head">
          <div>
            <strong>Consulta</strong>
            <span id="feature">${escapeHtml(avatar.feature)}</span>
          </div>
          <div class="console__head-actions">
            <button class="icon-btn" id="mute" type="button" aria-pressed="${state.muted}" title="Activar o silenciar voz">${state.muted ? "○ Voz" : "◉ Voz"}</button>
            <button class="icon-btn" id="replay" type="button" title="Repetir última frase">↺ Oír</button>
            <button class="icon-btn" id="reset" type="button" title="Nueva conversación">↻ Nueva</button>
          </div>
        </div>

        <div class="studio-alert" id="studio-alert" hidden role="status"></div>

        <div class="quick-actions${vision ? "" : " is-solo"}">
          <button class="ritual-btn" id="draw" type="button"><span aria-hidden="true">✦</span><b>Tirar una carta</b><small>un solo arcano mayor</small></button>
          ${vision ? `<button class="ritual-btn" id="vision" type="button"><span aria-hidden="true">◈</span><b>Opcional: tu foto</b><small>solo si quieres que mire algo tuyo</small></button>` : ""}
          <input id="image-input" type="file" accept="image/jpeg,image/png,image/webp" hidden />
        </div>

        <div class="image-preview" id="image-preview" hidden>
          <img id="preview-img" alt="Imagen seleccionada" />
          <div><strong>Imagen preparada</strong><span id="preview-name"></span></div>
          <button class="icon-btn" id="remove-image" type="button">Quitar</button>
        </div>

        <div class="transcript" id="transcript" aria-live="polite"></div>

        <div class="thinking" id="thinking" hidden><span></span><span></span><span></span><em>${escapeHtml(avatar.name)} interpreta…</em></div>

        <div class="suggestions" id="suggestions" role="group" aria-label="Sugerencias"></div>

        <form class="composer" id="composer">
          <label class="sr-only" for="input">Escribe tu consulta</label>
          <textarea id="input" rows="1" maxlength="8000" placeholder="Dile qué te inquieta. Un saludo no lanza cartas; pídele una tirada cuando quieras." autocomplete="off"></textarea>
          <button class="mic" id="mic" type="button" title="Hablar" aria-label="Dictar">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5.5 11a6.5 6.5 0 0 0 13 0"/><path d="M12 17.5V21"/></svg>
          </button>
          <button class="send" id="send" type="submit" title="Enviar" aria-label="Enviar">
            <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M3.4 20.6 21 12 3.4 3.4l.1 6.7L15 12 3.5 13.9z"/></svg>
          </button>
        </form>
        <p class="disclaimer">El tarot es simbólico, no un dictamen. ${escapeHtml(avatar.name)} tira una sola carta: no hace falta subir nada.</p>
      </section>
    </main>
  `;

  const transcript = root.querySelector("#transcript") as HTMLElement;
  addBubble(transcript, "bot", avatar.welcome);
  renderSuggestions(root, STARTERS);
  bindStudio(root);
  bindPresence(root);
  bindTranscript(transcript);
  void checkHealth(root);
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
    lastFailed = null;
    welcomePending = true;
    clearImage(root);
    stopAudio();
    renderStudio(root);
  });
  root.querySelector("#mute")?.addEventListener("click", (event) => {
    state.muted = !state.muted;
    const button = event.currentTarget as HTMLButtonElement;
    button.textContent = state.muted ? "○ Voz" : "◉ Voz";
    button.setAttribute("aria-pressed", String(state.muted));
    if (state.muted) stopAudio();
  });
  root.querySelector("#replay")?.addEventListener("click", () => {
    if (lastSpoken) {
      void speakLine(lastSpoken);
      return;
    }
    const host = root.querySelector("#studio-alert") as HTMLElement | null;
    if (!host || !host.hidden) return;
    host.hidden = false;
    host.className = "studio-alert is-soft";
    host.textContent = "Aún no hay frase para repetir.";
    window.setTimeout(() => {
      if (host.textContent === "Aún no hay frase para repetir.") {
        host.hidden = true;
        host.replaceChildren();
      }
    }, 2200);
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
  input.addEventListener("input", () => resizeInput(input));
  root.querySelector("#suggestions")?.addEventListener("click", (event) => {
    const button = (event.target as HTMLElement).closest("button[data-prompt]") as HTMLButtonElement | null;
    if (!button || state.busy) return;
    const text = button.dataset.prompt ?? "";
    const draw = button.dataset.draw === "1";
    if (!text) return;
    input.value = text;
    resizeInput(input);
    if (draw) void drawCards(root);
    else void send(root);
  });
  root.querySelector("#transcript")?.addEventListener("click", (event) => {
    const retry = (event.target as HTMLElement).closest("[data-retry]") as HTMLButtonElement | null;
    if (!retry || state.busy || !lastFailed) return;
    const { text, draw } = lastFailed;
    lastFailed = null;
    (root.querySelector("#input") as HTMLTextAreaElement).value = text;
    if (draw) void drawCards(root);
    else void send(root);
  });
  bindMic(root);
}

function bindPresence(root: HTMLElement): void {
  const video = root.querySelector(".presence__video") as HTMLVideoElement | null;
  const clips = state.avatar ? clipsFor(state.avatar) : [];
  const gen = ++presenceGen;
  const live = () => gen === presenceGen;
  if (!video || !clips.length || prefersReducedMotion()) {
    revealOrb(root);
    maybeWelcome();
    return;
  }
  let index = 0;
  let loops = 0;
  let gapTimer = 0;
  const stillActive = () => live() && !root.querySelector(".presence")?.classList.contains("is-orb");
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
    frameVideo(video, clip.id, state.avatar?.id ?? "arcana");
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
  video.addEventListener("error", () => startClip(index + 1));
  startClip(0);
  window.setTimeout(() => {
    if (!live()) return;
    revealOrb(root);
    maybeWelcome();
  }, 40000);
}

function frameVideo(video: HTMLVideoElement, clipId: string, avatarId: string): void {
  if (clipId === "wizard") {
    video.style.objectPosition = "50% 42%";
    video.style.transform = "scale(1.08)";
    video.style.transformOrigin = "50% 46%";
    return;
  }
  if (avatarId === "arcano") {
    video.style.objectPosition = "42% 36%";
    video.style.transform = "scale(1.1)";
    video.style.transformOrigin = "42% 38%";
    return;
  }
  video.style.objectPosition = "50% 12%";
  video.style.transform = "scale(1.22)";
  video.style.transformOrigin = "50% 16%";
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
  root.querySelector(".arcana")?.classList.add("is-orb");
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
    button.setAttribute("aria-pressed", "true");
  };
  rec.onend = () => {
    live = false;
    button.classList.remove("is-live");
    button.title = "Hablar";
    button.setAttribute("aria-pressed", "false");
  };
  rec.onerror = () => {
    live = false;
    button.classList.remove("is-live");
    button.setAttribute("aria-pressed", "false");
  };
  rec.onresult = (event) => {
    const input = root.querySelector("#input") as HTMLTextAreaElement;
    const chunks: string[] = [];
    for (let i = 0; i < event.results.length; i += 1) {
      chunks.push(event.results[i][0].transcript);
    }
    input.value = chunks.join(" ").trim();
    resizeInput(input);
    const last = event.results[event.results.length - 1];
    if (last?.isFinal && input.value) void send(root);
  };
}

function renderSuggestions(root: HTMLElement, chips: PromptChip[]): void {
  const wrap = root.querySelector("#suggestions");
  if (!wrap) return;
  const usable = chips.filter((chip) => chip.text.trim());
  wrap.hidden = usable.length === 0;
  wrap.innerHTML = usable
    .map((chip) => `<button type="button" data-prompt="${escapeHtml(chip.text)}" data-draw="${chip.draw ? "1" : "0"}">${escapeHtml(chip.label)}</button>`)
    .join("");
}

function resetConversation(root: HTMLElement): void {
  if (state.busy || !state.avatar) return;
  state.conversationId = null;
  lastFailed = null;
  clearImage(root);
  stopAudio();
  const transcript = root.querySelector("#transcript") as HTMLElement;
  transcript.replaceChildren();
  addBubble(transcript, "bot", state.avatar.welcome);
  renderSuggestions(root, STARTERS);
  const input = root.querySelector("#input") as HTMLTextAreaElement;
  input.value = "";
  resizeInput(input);
  input.focus();
  welcomePending = false;
  void speakLine(state.avatar.welcome);
}

function selectImage(root: HTMLElement, event: Event): void {
  const input = event.currentTarget as HTMLInputElement;
  const file = input.files?.[0] ?? null;
  if (!file) return;
  state.selectedImage = file;
  if (previewObjectUrl) URL.revokeObjectURL(previewObjectUrl);
  previewObjectUrl = URL.createObjectURL(file);
  const preview = root.querySelector("#image-preview") as HTMLElement;
  const img = root.querySelector("#preview-img") as HTMLImageElement;
  const name = root.querySelector("#preview-name") as HTMLElement;
  img.src = previewObjectUrl;
  name.textContent = `${file.name} · ${(file.size / 1024 / 1024).toFixed(1)} MB`;
  preview.hidden = false;
  (root.querySelector("#input") as HTMLTextAreaElement).placeholder = `¿Qué quieres que ${state.avatar?.name ?? "el avatar"} observe en esta imagen?`;
}

function clearImage(root: HTMLElement): void {
  state.selectedImage = null;
  if (previewObjectUrl) {
    URL.revokeObjectURL(previewObjectUrl);
    previewObjectUrl = null;
  }
  const input = root.querySelector("#image-input") as HTMLInputElement | null;
  if (input) input.value = "";
  const preview = root.querySelector("#image-preview") as HTMLElement | null;
  if (preview) preview.hidden = true;
  const text = root.querySelector("#input") as HTMLTextAreaElement | null;
  if (text) text.placeholder = "Dile qué te inquieta. Un saludo no lanza cartas; pídele una tirada cuando quieras.";
}

async function drawCards(root: HTMLElement): Promise<void> {
  if (state.busy || !state.avatar) return;
  const input = root.querySelector("#input") as HTMLTextAreaElement;
  const question = input.value.trim() || "Haz una nueva tirada de una carta para el tema que estamos explorando.";
  input.value = "";
  resizeInput(input);
  await runChat(root, question, true);
}

async function send(root: HTMLElement): Promise<void> {
  if (state.busy || !state.avatar) return;
  const input = root.querySelector("#input") as HTMLTextAreaElement;
  const text = input.value.trim();
  if (!text && !state.selectedImage) return;
  input.value = "";
  resizeInput(input);

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
  return /\b(tirada|tarot|cartas|lectura|tira(r|me)? las cartas|otra tirada|haz(me)? una (tirada|lectura)|lanza(me)? (una )?tirada|una carta)\b/.test(t);
}

async function runChat(root: HTMLElement, text: string, draw: boolean): Promise<void> {
  if (!state.avatar) return;
  const transcript = root.querySelector("#transcript") as HTMLElement;
  lastFailed = null;
  setBusy(root, true);
  addBubble(transcript, "user", draw ? `✦ ${text}` : text);
  const bot = addBubble(transcript, "bot", "");
  let failed = false;

  try {
    await streamChat(text, state.avatar.id, state.conversationId, {
      onMeta: (id) => { state.conversationId = id; },
      onToken: (token) => {
        bot.textContent = (bot.textContent ?? "") + token;
        stickTranscript(transcript);
        if (state.busy && !playing) setPresence("writing");
      },
      onAudio: (url) => enqueueAudio(url),
      onImage: (url, caption, cards, replace) => addSpread(transcript, url, caption, cards, replace),
      onError: (code, message) => {
        failed = true;
        lastFailed = { text, draw };
        addError(transcript, explain(code, message));
      },
    }, undefined, draw);
  } catch {
    failed = true;
    lastFailed = { text, draw };
    addError(transcript, "No hay conexión con el estudio (127.0.0.1:8000). ¿Sigue FastAPI en marcha?");
  } finally {
    if (!bot.textContent?.trim()) bot.closest(".bubble")?.remove();
    else lastSpoken = bot.textContent;
    renderSuggestions(root, failed && lastFailed ? retryChips() : FOLLOWUPS);
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
    addError(transcript, error instanceof Error ? error.message : "No se pudo analizar la imagen.");
    renderSuggestions(root, FOLLOWUPS);
  } finally {
    setBusy(root, false);
  }
}

function retryChips(): PromptChip[] {
  return [{ label: "Reintentar", text: lastFailed?.text ?? "", draw: lastFailed?.draw }];
}

function setBusy(root: HTMLElement, busy: boolean): void {
  state.busy = busy;
  (root.querySelector("#send") as HTMLButtonElement).disabled = busy;
  (root.querySelector("#draw") as HTMLButtonElement).disabled = busy;
  const vision = root.querySelector("#vision") as HTMLButtonElement | null;
  if (vision) vision.disabled = busy;
  (root.querySelector("#mic") as HTMLButtonElement).disabled = busy;
  (root.querySelector("#thinking") as HTMLElement).hidden = !busy;
  root.querySelector(".console")?.setAttribute("aria-busy", String(busy));
  root.querySelectorAll("#avatar-switch button").forEach((btn) => {
    (btn as HTMLButtonElement).disabled = busy;
  });
  const reset = root.querySelector("#reset") as HTMLButtonElement | null;
  if (reset) reset.disabled = busy;
  const input = root.querySelector("#input") as HTMLTextAreaElement | null;
  if (input) input.disabled = busy;
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
  stickTranscript(transcript);
  return content;
}

function addError(transcript: HTMLElement, text: string): void {
  const content = addBubble(transcript, "error", text);
  if (!lastFailed) return;
  const retry = document.createElement("button");
  retry.type = "button";
  retry.className = "bubble__retry";
  retry.dataset.retry = "1";
  retry.textContent = "Reintentar";
  content.parentElement?.append(retry);
}

function addSpread(
  transcript: HTMLElement,
  url: string,
  caption: string,
  cards?: Array<{ position: string; name: string }>,
  replace = false,
): void {
  if (replace) {
    const existing = transcript.querySelector("figure.spread:last-of-type") as HTMLElement | null;
    const img = existing?.querySelector("img");
    if (existing && img) {
      img.src = url;
      img.alt = caption || "Carta de tarot";
      const strong = existing.querySelector("figcaption strong");
      if (strong) strong.textContent = caption || "La carta";
      return;
    }
  }
  const wrap = document.createElement("figure");
  wrap.className = "spread";
  const frame = document.createElement("div");
  frame.className = "spread__frame";
  const img = document.createElement("img");
  img.src = url;
  img.alt = caption || "Carta de tarot";
  img.loading = "lazy";
  frame.append(img);
  wrap.append(frame);
  const fig = document.createElement("figcaption");
  fig.innerHTML = `<strong>${escapeHtml(caption || "La carta")}</strong>`;
  if (cards?.length) {
    const list = document.createElement("div");
    list.className = "spread__cards";
    for (const card of cards) {
      const chip = document.createElement("span");
      chip.textContent = card.name;
      list.append(chip);
    }
    fig.append(list);
  }
  wrap.append(fig);
  transcript.append(wrap);
  const pin = () => stickTranscript(transcript);
  img.addEventListener("load", pin);
  img.addEventListener("error", () => {
    frame.classList.add("is-missing");
    const fallback = document.createElement("p");
    fallback.className = "spread__fallback";
    fallback.textContent = "La visión no llegó. El nombre de la carta está abajo; la lectura sigue.";
    img.replaceWith(fallback);
  });
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
  img.addEventListener("error", () => {
    img.replaceWith(Object.assign(document.createElement("p"), {
      className: "spread__fallback",
      textContent: "No pude mostrar esa foto. Puedes describirla en el chat.",
    }));
  });
  transcript.append(wrap);
  stickTranscript(transcript);
}

function bindTranscript(transcript: HTMLElement): void {
  transcript.dataset.stick = "1";
  transcript.addEventListener("scroll", () => {
    const room = transcript.scrollHeight - transcript.scrollTop - transcript.clientHeight;
    transcript.dataset.stick = room < 72 ? "1" : "0";
  });
  const observer = new MutationObserver(() => stickTranscript(transcript));
  observer.observe(transcript, { childList: true, subtree: true, characterData: true });
}

function stickTranscript(transcript: HTMLElement): void {
  if (transcript.dataset.stick === "0") return;
  transcript.scrollTop = transcript.scrollHeight;
}

function resizeInput(input: HTMLTextAreaElement): void {
  input.style.height = "auto";
  input.style.height = `${Math.min(Math.max(input.scrollHeight, 40), 132)}px`;
}

async function checkHealth(root: HTMLElement): Promise<void> {
  const host = root.querySelector("#studio-alert") as HTMLElement | null;
  if (!host) return;
  try {
    const health = await fetchHealth();
    if (!health.ollama || !health.ollama_chat_ready) {
      host.hidden = false;
      host.className = "studio-alert";
      host.innerHTML = "<strong>El intérprete local no responde.</strong> Arráncalo con scripts/start-ollama.ps1. Hasta entonces no podrá leer.";
      return;
    }
    if (!health.piper_executable) {
      host.hidden = false;
      host.className = "studio-alert is-soft";
      host.innerHTML = "<strong>La voz no está lista.</strong> Puedes leer la consulta; el audio llegará cuando la voz local esté disponible.";
      return;
    }
    host.hidden = true;
    host.replaceChildren();
  } catch {
    host.hidden = false;
    host.className = "studio-alert";
    host.innerHTML = "<strong>No pude leer el estado del estudio.</strong> Recarga con Ctrl+F5 si el chat se queda mudo.";
  }
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
    idle: "escucha",
    thinking: "en trance",
    writing: "dictando",
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
  if (code === "backend_unavailable" || code === "http_error") {
    return "El estudio no responde. Comprueba que FastAPI sigue en 127.0.0.1:8000.";
  }
  if (code === "ollama_unavailable") {
    return "El intérprete local no responde. Arráncalo en esta máquina (scripts/start-ollama.ps1).";
  }
  if (code === "ollama_vision_unavailable") {
    return "La mirada a fotos no está lista ahora. Puedes seguir con la tirada sin subir nada.";
  }
  if (code === "piper_unavailable") {
    return "La voz no está lista en esta máquina. Puedes seguir leyendo.";
  }
  return message;
}

function prefersReducedMotion(): boolean {
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

function escapeHtml(value: string): string {
  return value.replace(/[&<>'"]/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" })[char] ?? char);
}

function gateHtml(): string {
  return `<div class="gate" role="dialog" aria-labelledby="gate-title" aria-describedby="gate-lede">
    <video class="gate__video" autoplay muted loop playsinline poster="/media/image/arcana.jpg?v=land" src="/media/videos/portada.mp4" aria-hidden="true"></video>
    <div class="gate__veil"></div>
    <div class="gate__copy">
      <div class="gate__orb">${orbMarkup()}</div>
      <p class="gate__kicker">Consulta privada</p>
      <h1 id="gate-title">Arcana</h1>
      <p class="gate__lede" id="gate-lede">Una sola carta. Una voz. Aquí, en tu máquina. Pregunta; ella tira.</p>
      <button class="enter" id="enter" type="button">Entrar</button>
      <small class="gate__note">Nada sale de tu máquina · 127.0.0.1</small>
    </div>
  </div>`;
}

function errorGate(kind: string): string {
  const copy =
    kind === "avatar"
      ? { kicker: "Catálogo", lede: "Arcana no está en el catálogo de avatares. Revisa la carpeta avatars/." }
      : {
          kicker: "Sin conexión",
          lede: "No puedo abrir el estudio. Comprueba que FastAPI está en 127.0.0.1:8000 y recarga.",
        };
  return `<div class="gate gate--error">
    <div class="gate__copy">
      <div class="gate__orb">${orbMarkup()}</div>
      <p class="gate__kicker">${copy.kicker}</p>
      <h1>Arcana</h1>
      <p class="gate__lede">${copy.lede}</p>
      <button class="enter" id="retry" type="button">Reintentar</button>
      <small class="gate__note">Salud: 127.0.0.1:8000/health · Ollama: scripts/start-ollama.ps1</small>
    </div>
  </div>`;
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
