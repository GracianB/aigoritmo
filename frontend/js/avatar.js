import { CONFIG } from "./config.js";
import { getAvatarAssets } from "./api.js";

const STATES = {
  idle: ["IDLE", "READY TO EXPLORE"],
  thinking: ["THINKING", "INTERPRETING"],
  talking: ["TALKING", "SHARING INSIGHT"],
  listening: ["LISTENING", "WAITING FOR YOU"],
  error: ["ERROR", "CONNECTION ISSUE"]
};

export class AvatarController {
  constructor() {
    this.stage = document.querySelector("#avatarStage");
    this.label = document.querySelector("#avatarStateLabel");
    this.description = document.querySelector("#avatarStateDescription");
    this.video = document.querySelector("#avatarVideo");
    this.fallback = document.querySelector("#avatarFallback");
    this.currentState = "idle";
    this.stateAssets = {};
    this.video?.addEventListener("error", () => this.useFallback());
    this.fallback?.addEventListener("error", () => this.createFallbackVisual());
    this.loadAssets();
  }

  apiUrl(path) { return path.startsWith("http") ? path : `${CONFIG.API_BASE_URL}${path}`; }

  async loadAssets() {
    try {
      const { assets = [] } = await getAvatarAssets("arcana");
      const video = assets.find(a => a.kind === "video" && /idle/i.test(a.name)) || assets.find(a => a.kind === "video");
      const image = assets.find(a => a.kind === "image" && /avatar|idle|arcana/i.test(a.name)) || assets.find(a => a.kind === "image");
      if (video && this.video) {
        this.video.src = this.apiUrl(video.url);
        this.video.style.display = "block";
        this.video.load();
      } else if (image && this.fallback) {
        this.fallback.src = this.apiUrl(image.url);
        this.useFallback();
      } else {
        this.useFallback();
      }
    } catch {
      this.useFallback();
    }
  }

  useFallback() {
    if (this.video) this.video.style.display = "none";
    if (this.fallback) this.fallback.style.display = "block";
    if (!this.fallback?.getAttribute("src")) this.createFallbackVisual();
  }

  createFallbackVisual() {
    if (!this.fallback) return;
    this.fallback.style.display = "none";
    let node = this.stage.querySelector(".generated-avatar-fallback");
    if (!node) {
      node = document.createElement("div");
      node.className = "generated-avatar-fallback";
      node.innerHTML = '<div class="generated-avatar-glyph">A</div><div>ARCANA</div><small>SPECIALIZED AI</small>';
      this.stage.querySelector("#avatarMedia")?.appendChild(node);
    }
  }

  setState(state) {
    if (!STATES[state]) return;
    this.stage.className = `avatar-stage state-${state}`;
    this.currentState = state;
    this.label.textContent = STATES[state][0];
    this.description.textContent = STATES[state][1];
    window.dispatchEvent(new CustomEvent("aigoritmo:avatar", { detail: { state, timestamp: Date.now() } }));
  }
}
