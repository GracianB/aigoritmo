
export class SpeechController {
  constructor() {
    this.enabled = false;
    this.synth = window.speechSynthesis;
  }

  toggle() {
    this.enabled = !this.enabled;
    if (!this.enabled) this.synth?.cancel();
    return this.enabled;
  }

  speak(text) {
    if (!this.enabled || !this.synth || !("SpeechSynthesisUtterance" in window)) return;
    this.synth.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "es-ES";
    utterance.rate = 1;
    this.synth.speak(utterance);
  }
}
