<div align="center">

<a href="http://127.0.0.1:8000">
<img
src="https://capsule-render.vercel.app/api?type=waving&height=260&color=0:030303,35:0D0A07,70:21170D,100:050505&text=AIGORITMO&fontColor=E1BD78&fontSize=64&fontAlignY=38&desc=ARCANA%20%C2%B7%20ARCANO&descColor=F4EEE4&descAlignY=62&descSize=23&animation=twinkling"
width="100%"
alt="Aigoritmo · Arcana · Arcano"
/>
</a>

<br>

<img
src="https://readme-typing-svg.demolab.com?font=Fraunces&weight=500&size=27&duration=3200&pause=850&color=C9A86A&center=true&vCenter=true&width=1000&height=65&lines=One+card.+One+presence.+One+answer.;ARCANA+%C2%B7+GOLD+%2F+VELVET;ARCANO+%C2%B7+STEEL+%2F+NIGHT;Local+Piper+%C2%B7+Swappable+Brain;A+cinematic+Spanish-first+local+studio."
alt="Aigoritmo typing"
/>

<br>

<a href="#experience">
<img src="https://img.shields.io/badge/EXPERIENCE-ARCANA%20%C2%B7%20ARCANO-C9A86A?style=for-the-badge&labelColor=090909" alt="Experience"/>
</a>
<a href="#architecture">
<img src="https://img.shields.io/badge/ARCHITECTURE-LOCAL--FIRST-8E7A5A?style=for-the-badge&labelColor=090909" alt="Architecture"/>
</a>
<a href="#quick-start">
<img src="https://img.shields.io/badge/RUN-LOCAL-7EE7FF?style=for-the-badge&labelColor=090909" alt="Run locally"/>
</a>

<br><br>

**ONE CARD · TWO PRESENCES · LOCAL VOICE · SWAPPABLE BRAIN**

<br>

<sub>
Aigoritmo is a cinematic local studio built around a deliberately constrained interaction:
<br>
<strong>one consultation → one card → one answer.</strong>
</sub>

</div>

---

## ◈ EXPERIENCE

> **Aigoritmo is not a generic chatbot.**
>
> It is a controlled conversational experience where visual presence, voice, card logic and language work as a single system.

The interface is built around two finished identities:

| Presence      | Visual language          | Character                     |
| ------------- | ------------------------ | ----------------------------- |
| 🜂 **ARCANA** | Gold · Velvet · Warmth   | Intuitive, luminous, intimate |
| ⚔ **ARCANO**  | Steel · Night · Contrast | Grave, restrained, nocturnal  |

No avatar catalogue.
No endless character selector.
No three-card spread.

Just **two presences** with a defined visual and conversational identity.

---

## ✦ THE CORE RULE

### ONE CONSULTATION = ONE CARD

Aigoritmo deliberately avoids the traditional:

`PAST → PRESENT → FUTURE`

and instead follows:

```text
CONSULTATION
     │
     ▼
  ONE CARD
     │
     ▼
 ONE READING
     │
     ▼
 ONE ANSWER
```

The restriction is intentional.

The system is designed to make each interaction feel like an event rather than a data dump.

### The rules

| Rule            | Behaviour                                              |
| --------------- | ------------------------------------------------------ |
| 👋 Greeting     | Does **not** trigger a draw                            |
| 🃏 Consultation | Produces exactly **one card**                          |
| 🔮 Reading      | Built around the selected card                         |
| 🎙 Voice        | Generated locally through Piper                        |
| 🧠 Brain        | Ollama, Grok or ChatGPT                                |
| 🎨 Image        | Local card first, Pollinations as optional replacement |
| 👤 Identity     | User sees the presence, not the underlying model       |

---

## ◇ THE TWO PRESENCES

### 🜂 ARCANA

```text
GOLD
VELVET
WARMTH
INTUITION
```

Arcana is the warmer presence.

Its visual language is built around:

* gold
* velvet
* warm shadows
* cinematic lighting
* intimate atmosphere
* softer transitions

It should feel like entering a private reading room.

---

### ⚔ ARCANO

```text
STEEL
NIGHT
CONTRAST
GRAVITY
```

Arcano moves in the opposite direction.

Its language is:

* steel
* darkness
* cold contrast
* restrained movement
* deeper atmosphere
* stronger visual tension

Same system.

Different presence.

---

## ◉ THE ORB

The interface uses a central **presence orb** as a visual state indicator.

It is not decoration.

The orb communicates that the system is:

```text
IDLE
  ↓
LISTENING
  ↓
THINKING
  ↓
READING
  ↓
SPEAKING
```

The goal is to make system state perceptible without turning the interface into a conventional dashboard.

---

## ⇄ PRESENCE TRANSITIONS

Changing between Arcana and Arcano is treated as a transition between identities rather than a simple UI toggle.

```text
ARCANA
  │
  │  FADE
  ▼
TRANSITION
  │
  │  PRESENCE CHANGE
  ▼
ARCANO
```

The avatar changes with a visual fade so the interface preserves continuity.

---

# 🃏 CARD SYSTEM

The card layer is deliberately resilient.

### Primary path

```text
USER
 │
 ▼
LOCAL CARD
 │
 ▼
IMMEDIATE EXPERIENCE
```

The card is available locally without waiting for external image generation.

### Optional visual replacement

```text
LOCAL CARD
    │
    ├──────────────► USE IMMEDIATELY
    │
    ▼
POLLINATIONS
    │
    ▼
OPTIONAL GENERATED IMAGE
```

Pollinations can replace the local visual in approximately **8 seconds**.

The important architectural principle is:

> **External image generation is optional. The experience is not.**

---

# 🧠 SWAPPABLE BRAIN

Aigoritmo separates the conversational brain from the experience layer.

```text
                    ┌─────────────┐
                    │   AIGORITMO │
                    │  EXPERIENCE │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
          OLLAMA         GROK        CHATGPT
          LOCAL           API          API
              │            │            │
              └────────────┼────────────┘
                           ▼
                    SAME EXPERIENCE
```

The model can change.

The identity does not.

The card system does not.

The voice system does not.

The interface does not.

---

## 🔌 PROVIDER MATRIX

| Provider             | Brain | Voice       | Card  |
| -------------------- | ----- | ----------- | ----- |
| **Ollama**           | Local | Piper local | Local |
| **Grok / xAI**       | API   | Piper local | Local |
| **ChatGPT / OpenAI** | API   | Piper local | Local |

This separation makes experimentation possible without rebuilding the product around every model provider.

---

# 🎙 LOCAL VOICE

Voice is handled through **Piper**.

```text
LLM RESPONSE
     │
     ▼
    TEXT
     │
     ▼
   PIPER
     │
     ▼
   VOICE
```

The voice layer remains independent from the LLM.

That means changing the brain does not require changing the voice.

---

# 🏗 ARCHITECTURE

```text
┌───────────────────────────────────────────────┐
│                   AIGORITMO                   │
├───────────────────────────────────────────────┤
│                                               │
│  EXPERIENCE                                   │
│  ├── Arcana                                   │
│  ├── Arcano                                   │
│  ├── Presence Orb                             │
│  └── Avatar Transitions                       │
│                                               │
│  CONSULTATION                                 │
│  ├── User Input                               │
│  ├── One-Card Rule                            │
│  └── Reading Generation                       │
│                                               │
│  BRAIN                                        │
│  ├── Ollama                                   │
│  ├── Grok                                     │
│  └── OpenAI                                   │
│                                               │
│  VOICE                                        │
│  └── Piper                                     │
│                                               │
│  VISUALS                                      │
│  ├── Local Cards                              │
│  └── Pollinations                             │
│                                               │
└───────────────────────────────────────────────┘
```

---

# ⚡ DATA FLOW

```text
USER
 │
 ▼
CONSULTATION
 │
 ▼
AIGORITMO
 │
 ├──────────────► CARD
 │
 ├──────────────► LLM
 │                  │
 │                  ▼
 │               READING
 │
 └──────────────► PIPER
                    │
                    ▼
                  VOICE
```

Everything converges into one experience.

---

# 🚀 QUICK START

### 1. Start the local studio

```powershell
powershell -File X:\GitHub\systems-lab\aigoritmo\PROBAR-ARCANA.ps1
```

Then open:

```text
http://127.0.0.1:8000
```

Health endpoint:

```text
http://127.0.0.1:8000/health
```

Current version:

```text
2.1.0-definitiva
```

### Shortcut

```text
X:\PROBAR-ARCANA.bat
```

Detailed instructions:

```text
COMO-EJECUTAR.md
```

---

# 🔐 CONFIGURATION

Create your environment file from:

```text
.env.example
```

Then configure the provider you want to use.

> Never paste API keys into source code, README files or chat messages. Humanity has somehow survived this long while repeatedly putting passwords in screenshots, so let's not contribute another example.

---

## 🦙 OLLAMA

For a local-first setup:

```env
LLM_PROVIDER=ollama
```

No API key is required for the LLM provider.

Architecture:

```text
USER
 │
 ▼
AIGORITMO
 │
 ▼
OLLAMA
 │
 ▼
LOCAL RESPONSE
 │
 ▼
PIPER
```

---

## 🚀 GROK / xAI

Configure:

```env
LLM_PROVIDER=spacexai
XAI_API_KEY=...
```

The configuration already prefers the `spacexai` provider.

Architecture:

```text
USER
 │
 ▼
AIGORITMO
 │
 ▼
GROK / xAI
 │
 ▼
RESPONSE
 │
 ▼
PIPER LOCAL
```

---

## 🤖 CHATGPT / OPENAI

Configure:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=...
```

Architecture:

```text
USER
 │
 ▼
AIGORITMO
 │
 ▼
OPENAI
 │
 ▼
RESPONSE
 │
 ▼
PIPER LOCAL
```

---

# 🛡 LOCAL-FIRST DESIGN

Aigoritmo can operate with a strongly local architecture:

```text
┌─────────────────────┐
│      AIGORITMO      │
├─────────────────────┤
│                     │
│  Card        LOCAL  │
│  Voice       LOCAL  │
│  Interface   LOCAL  │
│  Brain       OLLAMA │
│                     │
└─────────────────────┘
```

When using Grok or OpenAI, only the brain layer moves to an external API.

The experience architecture remains the same.

---

# 🧩 SYSTEM PRINCIPLES

### 01 · CONSTRAINT

Less can create more presence.

### 02 · SEPARATION

The interface should not depend on a specific model.

### 03 · LOCALITY

Cards and voice should remain available locally.

### 04 · RESILIENCE

Optional external services should never define the entire experience.

### 05 · IDENTITY

Arcana and Arcano are finished presences, not skins.

### 06 · SIMPLICITY

One consultation should produce one meaningful interaction.

---

# 🧪 EXPERIENCE MATRIX

| Layer            | Local | Replaceable | External |
| ---------------- | :---: | :---------: | :------: |
| Interface        |   ✓   |             |          |
| Presence         |   ✓   |      ✓      |          |
| Card             |   ✓   |      ✓      | Optional |
| Voice            |   ✓   |      ✓      |          |
| Brain            |   ✓   |      ✓      | Optional |
| Image generation |       |      ✓      |     ✓    |

---

# 📡 SYSTEM STATUS

```text
AIGORITMO
────────────────────────────────────

VERSION       2.1.0-definitiva
MODE          LOCAL STUDIO
LANGUAGE      ESPAÑOL
PRESENCES     ARCANA · ARCANO
CARD MODE     ONE CARD
VOICE         PIPER
BRAIN         OLLAMA / GROK / OPENAI
IMAGE         LOCAL / POLLINATIONS
```

---

# 🜁 WHY "ARCANA · ARCANO"?

The names describe two different ways of inhabiting the same system.

**Arcana** is warmth.

**Arcano** is gravity.

They are not separate products.

They are two interpretations of the same machine.

```text
                 AIGORITMO
                     │
            ┌────────┴────────┐
            ▼                 ▼
         ARCANA             ARCANO
       GOLD / VELVET       STEEL / NIGHT
            │                 │
            └────────┬────────┘
                     ▼
                ONE SYSTEM
```

---

# 🧭 PROJECT PHILOSOPHY

Aigoritmo is intentionally theatrical.

Not because the system needs theatre to function.

Because interaction is not only computation.

It is also:

```text
TIMING
PRESENCE
VOICE
VISUAL LANGUAGE
CONTEXT
RESTRAINT
```

The objective is to make a local AI system feel like an environment rather than another rectangular chat window.

---

# 🧱 DESIGN DNA

```text
CINEMATIC
     +
LOCAL-FIRST
     +
AI-AGNOSTIC
     +
VOICE
     +
VISUAL PRESENCE
     +
CONTROLLED INTERACTION
```

The result is deliberately closer to a **digital studio** than a conventional chatbot.

---

# 🔗 SYSTEMS LAB

Aigoritmo belongs to the experimental side of the broader ecosystem:

```text
                    PERSONAL / PROFESSIONAL
                             │
                             ▼
                         GRACIANB
                             │
            ┌────────────────┼────────────────┐
            │                │                │
            ▼                ▼                ▼
      PROFESSIONAL       SYSTEMS LAB         YOGA
       EXPERIENCE            PLAY           PRESENCE
            │                │                │
            │        ┌───────┼────────┐       │
            │        ▼       ▼        ▼       │
            │     ARCANA   OHANA   VÓRTICE    │
            │                                  │
            └──────────────┬───────────────────┘
                           ▼
                     EXPERIMENTATION
```

---

## 🌐 ECOSYSTEM

<div align="center">

<a href="https://gracianb.github.io/GracianB/">
<img src="https://img.shields.io/badge/HUB-GracianB-C4A574?style=for-the-badge&labelColor=090909" alt="GracianB Hub"/>
</a>

<a href="https://gracianb.github.io/systems-lab/">
<img src="https://img.shields.io/badge/SYSTEMS%20LAB-PLAY-7EE7FF?style=for-the-badge&labelColor=090909" alt="Systems Lab"/>
</a>

<a href="https://gracianb.github.io/project-ohana/">
<img src="https://img.shields.io/badge/PROJECT-OHANA-FFB86B?style=for-the-badge&labelColor=090909" alt="Project Ohana"/>
</a>

<a href="https://vortex-gilt-xi.vercel.app/">
<img src="https://img.shields.io/badge/VÓRTICE-WEBGL-9B8CFF?style=for-the-badge&labelColor=090909" alt="Vórtice"/>
</a>

<a href="https://gracianb.github.io/yoga-instructor/">
<img src="https://img.shields.io/badge/YOGA-PRESENCE-7DCaa5?style=for-the-badge&labelColor=090909" alt="Yoga"/>
</a>

</div>

---

# ◇ THE FINAL CARD

<div align="center">

### ONE CARD.

### TWO PRESENCES.

### ONE LOCAL STUDIO.

<br>

**ARCANA · ARCANO**

`A cinematic AI experiment built around presence, voice and constraint.`

<br>

<a href="https://github.com/GracianB">
<img src="https://img.shields.io/badge/GITHUB-GRACIANB-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub"/>
</a>

<a href="https://www.linkedin.com/in/gracianbaena">
<img src="https://img.shields.io/badge/LINKEDIN-GRACIAN%20BAENA-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn"/>
</a>

</div>

---

<div align="center">

<img
src="https://capsule-render.vercel.app/api?type=waving&height=170&section=footer&color=0:050505,40:160F09,75:0D0A07,100:030303&fontColor=E1BD78&animation=twinkling"
width="100%"
alt="Aigoritmo footer"
/>

<br>

<sub>

**AIGORITMO · ARCANA · ARCANO**

<br>

`Built locally. Designed as a presence.`

<br><br>

© 2026 Gracián Baena

</sub>

</div>


<div align="center">

<!-- ═══════════════════════════════════════════════════════════════════════ -->

<!--                               HERO                                      -->

<!-- ═══════════════════════════════════════════════════════════════════════ -->

<a href="http://127.0.0.1:8000">

<img
src="https://capsule-render.vercel.app/api?type=waving&height=260&color=0:030303,35:0D0A07,70:21170D,100:050505&text=AIGORITMO&fontColor=E1BD78&fontSize=64&fontAlignY=38&desc=ARCANA%20%C2%B7%20ARCANO&descColor=F4EEE4&descAlignY=62&descSize=23&animation=twinkling"
width="100%"
alt="Aigoritmo · Arcana · Arcano"
/>

</a>

<br>

<img
src="https://readme-typing-svg.demolab.com?font=Fraunces&weight=500&size=27&duration=3200&pause=850&color=C9A86A&center=true&vCenter=true&width=1000&height=65&lines=Una+carta.+Una+presencia.+Una+respuesta.;ARCANA+%C2%B7+ORO+%2F+VELVET;ARCANO+%C2%B7+ACERO+%2F+NOCHE;Piper+local+%C2%B7+Cerebro+intercambiable;Un+estudio+local+cinematogr%C3%A1fico+en+espa%C3%B1ol."
alt="Aigoritmo typing"
/>

<br><br>

<a href="http://127.0.0.1:8000">
<img src="https://img.shields.io/badge/%E2%96%B6%20ENTRAR-ARCANA-C9A86A?style=for-the-badge&labelColor=050505" alt="Entrar en Arcana">
</a>

<a href="#-ejecución">
<img src="https://img.shields.io/badge/2.1.0-DEFINITIVA-8B7355?style=for-the-badge&labelColor=050505" alt="Version">
</a>

<a href="#-voz-local">
<img src="https://img.shields.io/badge/VOICE-PIPER%20LOCAL-7DC7A8?style=for-the-badge&labelColor=050505" alt="Piper local">
</a>

<a href="#-cerebro-intercambiable">
<img src="https://img.shields.io/badge/BRAIN-OLLAMA%20%7C%20GROK%20%7C%20OPENAI-9B8AFB?style=for-the-badge&labelColor=050505" alt="LLM">
</a>

<br><br>

<table>
<tr>
<td align="center"><b>01</b><br><sub>ONE CARD</sub></td>
<td align="center"><b>02</b><br><sub>TWO PRESENCES</sub></td>
<td align="center"><b>03</b><br><sub>LOCAL VOICE</sub></td>
<td align="center"><b>04</b><br><sub>SWAPPABLE BRAIN</sub></td>
</tr>
</table>

<br>

> ## **NO ES UN CHATBOT.**
>
> Es una presencia que responde.

<br>

</div>

---

<div align="center">

# ✦ ARCANA

### **ORO · VELVET · CALIDEZ**

`warm / intimate / luminous`

<br>

# ◇ ARCANO

### **ACERO · NOCHE · GRAVEDAD**

`dark / restrained / deep`

<br>

`ONE EXPERIENCE · TWO PRESENCES`

</div>

---

# ═══════════════════════════════════════

# 01 · LA EXPERIENCIA

# ═══════════════════════════════════════

## **Una carta.**

## **Una presencia.**

## **Una respuesta.**

Aigoritmo es un estudio local experimental construido alrededor de una idea muy concreta:

> **La tecnología no debería ser lo primero que percibes.**

No hay un catálogo infinito de avatares.

No hay un selector de modelos delante del usuario.

No hay una consola disfrazada de producto.

Hay:

```text
                    ┌──────────────────────┐
                    │       CONSULTA        │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │      PRESENCIA       │
                    │  ARCANA / ARCANO     │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │      UNA CARTA       │
                    │    ARCANO MAYOR      │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    INTERPRETACIÓN     │
                    │         LLM          │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │       VOZ PIPER       │
                    │        LOCAL          │
                    └──────────────────────┘
```

<div align="center">

### **La complejidad está detrás del telón.**

</div>

---

# ✦ 02 · EL MANIFIESTO

<div align="center">

```text
SALUDO
  ↓
NO TIRADA

CONSULTA
  ↓
1 CARTA

CARTA
  ↓
1 INTERPRETACIÓN

INTERPRETACIÓN
  ↓
1 VOZ

VOZ
  ↓
EXPERIENCIA
```

</div>

### Las reglas están cerradas.

| Regla      | Decisión                            |
| :--------- | :---------------------------------- |
| Saludo     | **No lanza tirada**                 |
| Consulta   | **Una carta**                       |
| Tirada     | **Nunca tres**                      |
| Carta      | **Local al instante**               |
| Imagen     | **Pollinations opcional**           |
| Voz        | **100% local**                      |
| Cerebro    | **Intercambiable**                  |
| Modelos    | **No visibles para el consultante** |
| Presencias | **Solo Arcana / Arcano**            |

> **Menos mecánica. Más presencia.**

---

# 🃏 03 · ONE CARD

<div align="center">

## `01 CONSULTA`

↓

## `01 CARTA`

↓

## `01 INTERPRETACIÓN`

↓

## `01 RESPUESTA`

</div>

No existe:

```text
❌ pasado / presente / futuro
❌ tres cartas
❌ cinco cartas
❌ tirada automática
❌ carta al saludar
❌ ruleta visible
❌ catálogo de personajes
```

Existe:

```text
✓ UNA CARTA
✓ UNA PRESENCIA
✓ UNA LECTURA
✓ UNA VOZ
```

La restricción es intencionada.

**La experiencia gana fuerza precisamente porque no intenta hacerlo todo.**

---

# ◈ 04 · DOS PRESENCIAS

<table>
<tr>
<td width="50%" align="center">

## ✦ ARCANA

<img src="https://img.shields.io/badge/ORO-C9A86A?style=for-the-badge&labelColor=080706">

<br><br>

**VELVET**

**CÁLIDA**

**ENVOLVENTE**

<br>

Presencia luminosa y cercana.

</td>

<td width="50%" align="center">

## ◇ ARCANO

<img src="https://img.shields.io/badge/ACERO-8FA6B8?style=for-the-badge&labelColor=070A0E">

<br><br>

**NOCHE**

**GRAVE**

**PROFUNDA**

<br>

Presencia sobria y contenida.

</td>
</tr>
</table>

<br>

```text
                  ARCANA                 ARCANO
                    │                       │
              ORO / VELVET            ACERO / NOCHE
                    │                       │
                    └──────────┬────────────┘
                               │
                               ▼
                         MISMO MOTOR
```

No son dos skins.

Son **dos atmósferas sobre una misma arquitectura**.

---

# ◉ 05 · EL ORBE

La interfaz utiliza un orbe de presencia como elemento central.

Su función no es simplemente estética.

Es una señal de estado.

```text
                 ┌──────────┐
                 │   IDLE   │
                 └────┬─────┘
                      │
                  consulta
                      │
                      ▼
                 ┌──────────┐
                 │ THINKING │
                 └────┬─────┘
                      │
                  respuesta
                      │
                      ▼
                 ┌──────────┐
                 │ SPEAKING │
                 └────┬─────┘
                      │
                    Piper
                      │
                      ▼
                 ┌──────────┐
                 │   IDLE   │
                 └──────────┘
```

El usuario no necesita ver:

```text
provider=openai
temperature=0.7
generating_audio=true
model=...
```

Eso pertenece al laboratorio.

No al salón.

---

# 🎭 06 · CAMBIO DE PRESENCIA

Arcana → Arcano.

Arcano → Arcana.

Sin salto brusco.

```text
ARCANA
  │
  │  FADE OUT
  ▼
NEUTRAL
  │
  │  FADE IN
  ▼
ARCANO
```

### **Misma arquitectura.**

### **Otra presencia.**

---

# 🜂 07 · LA CARTA LOCAL

La carta debe existir **antes** de depender de cualquier generación externa.

```text
                 ┌────────────────┐
                 │  CARTA LOCAL   │
                 │                │
                 │   INSTANTÁNEA  │
                 └───────┬────────┘
                         │
                         │ opcional
                         ▼
                 ┌────────────────┐
                 │  POLLINATIONS  │
                 │                │
                 │     ~8s        │
                 └────────────────┘
```

### Arquitectura:

**Local first.**

La generación remota puede mejorar la representación.

No puede bloquear la experiencia.

---

# 🧠 08 · CEREBRO INTERCAMBIABLE

El LLM no define la identidad de Arcana.

Tampoco la de Arcano.

El proveedor es infraestructura.

```text
                         EXPERIENCIA
                              │
                              ▼
                     ┌────────────────┐
                     │  LLM ROUTER    │
                     └───────┬────────┘
                             │
             ┌───────────────┼───────────────┐
             │               │               │
             ▼               ▼               ▼
          OLLAMA            GROK          CHATGPT
          LOCAL             xAI            OPENAI
```

### `LLM_PROVIDER`

```env
LLM_PROVIDER=ollama
```

o:

```env
LLM_PROVIDER=spacexai
XAI_API_KEY=...
```

o:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=...
```

### La experiencia no cambia.

```text
OLLAMA ─┐
GROK   ─┼──► TEXTO ─► PIPER ─► VOZ
OPENAI ─┘
```

Eso es importante:

**el cerebro puede cambiar sin reconstruir la presencia.**

---

# 🔊 09 · VOZ LOCAL

<div align="center">

<img src="https://img.shields.io/badge/PIPER-100%25%20LOCAL-7DC7A8?style=for-the-badge&labelColor=07100B">

<br><br>

### `TEXT → PIPER → AUDIO`

</div>

Piper se encarga de la voz.

El LLM genera texto.

La máquina genera el audio.

```text
              LLM
               │
               │ texto
               ▼
          ┌──────────┐
          │  PIPER   │
          └────┬─────┘
               │
               │ audio
               ▼
          PRESENCIA
```

La voz no necesita conocer el proveedor del cerebro.

---

# 🏛 10 · ARQUITECTURA

```text
╔══════════════════════════════════════════════════════════╗
║                      AIGORITMO                           ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  EXPERIENCE                                             ║
║  ──────────────────────────────────────────────────────  ║
║  Presence · Card · Chat · Orbe · Atmosphere             ║
║                                                          ║
║                         │                                ║
║                         ▼                                ║
║                                                          ║
║  INTELLIGENCE                                           ║
║  ──────────────────────────────────────────────────────  ║
║  Ollama · Grok · OpenAI                                 ║
║                                                          ║
║                         │                                ║
║                         ▼                                ║
║                                                          ║
║  VOICE                                                  ║
║  ──────────────────────────────────────────────────────  ║
║  Piper · Local                                          ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
```

### Separación deliberada

```text
EXPERIENCE
     ≠
INTELLIGENCE
     ≠
VOICE
     ≠
CARD
```

Cada capa puede evolucionar.

La experiencia no tiene que hacerlo con ella.

---

# ⚡ 11 · QUICK START

<div align="center">

### **RUN THE STUDIO**

</div>

```powershell
powershell -File X:\GitHub\systems-lab\aigoritmo\PROBAR-ARCANA.ps1
```

### Abrir

```text
http://127.0.0.1:8000
```

### Health

```text
http://127.0.0.1:8000/health
```

### Versión

```json
{
  "version": "2.1.0-definitiva"
}
```

### Atajo

```text
X:\PROBAR-ARCANA.bat
```

### Documentación

```text
COMO-EJECUTAR.md
```

---

# 🔐 12 · CONFIGURACIÓN

```powershell
Copy-Item .env.example .env
```

<details>
<summary><b>01 · OLLAMA · LOCAL</b></summary>

```env
LLM_PROVIDER=ollama
```

No requiere:

```env
XAI_API_KEY
OPENAI_API_KEY
```

</details>

<details>
<summary><b>02 · GROK · xAI</b></summary>

```env
LLM_PROVIDER=spacexai
XAI_API_KEY=...
```

El YAML ya prioriza `spacexai`.

</details>

<details>
<summary><b>03 · CHATGPT · OPENAI</b></summary>

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=...
```

</details>

<details>
<summary><b>⚠ SECURITY · API KEYS</b></summary>

Nunca publiques claves reales.

Nunca las introduzcas en:

```text
README.md
issues
commits
screenshots
logs
```

Usa exclusivamente `.env`.

</details>

---

# 🧬 13 · PIPELINE

<div align="center">

```text
┌───────────┐
│ CONSULTA  │
└─────┬─────┘
      │
      ▼
┌───────────┐
│ PRESENCIA │
└─────┬─────┘
      │
      ▼
┌───────────┐
│ 1 CARTA   │
│   LOCAL   │
└─────┬─────┘
      │
      ▼
┌───────────┐
│    LLM    │
└─────┬─────┘
      │
      ▼
┌───────────┐
│ TEXTO     │
└─────┬─────┘
      │
      ▼
┌───────────┐
│   PIPER   │
└─────┬─────┘
      │
      ▼
┌───────────┐
│    VOZ    │
└─────┬─────┘
      │
      ▼
┌───────────┐
│ EXPERIENCIA│
└───────────┘
```

</div>

---

# 🕯 14 · THE SALON

La interfaz está diseñada como un espacio.

No como un panel.

No como un dashboard.

No como una demo técnica.

### El objetivo:

```text
        TECNOLOGÍA
             │
             │
             ▼
        DESAPARECE
             │
             ▼
        PRESENCIA
             │
             ▼
        ATENCIÓN
```

El chat ocupa el espacio principal.

El orbe funciona como punto de presencia.

La carta funciona como objeto central.

El cambio de avatar sucede mediante transición.

La voz completa el ciclo.

---

# 🧪 15 · ESTADO

<div align="center">

| SISTEMA          |       ESTADO       |
| :--------------- | :----------------: |
| **Arcana**       |     🟢 DEFINIDA    |
| **Arcano**       |     🟢 DEFINIDA    |
| **One Card**     |     🟢 CERRADO     |
| **Carta local**  |      🟢 ACTIVA     |
| **Pollinations** |     🟢 OPCIONAL    |
| **Piper**        |      🟢 LOCAL      |
| **Ollama**       |    🟢 DISPONIBLE   |
| **Grok**         |    🟢 DISPONIBLE   |
| **OpenAI**       |    🟢 DISPONIBLE   |
| **Orbe**         |      🟢 ACTIVO     |
| **Fundido**      |      🟢 ACTIVO     |
| **Versión**      | `2.1.0-definitiva` |

</div>

---

# ✦ 16 · POR QUÉ EXISTE

No para demostrar que un LLM puede contestar.

Eso ya lo sabemos.

El experimento es:

> **¿Puede una IA convertirse en presencia sin comportarse visualmente como una IA?**

Por eso:

```text
MODEL       → oculto
PROVIDER    → oculto
TOKENS      → ocultos
PIPELINE    → oculto

PRESENCE    → visible
CARD        → visible
VOICE       → visible
ATMOSPHERE  → visible
```

La inteligencia sigue ahí.

Simplemente no necesita ponerse una camiseta que diga:

**“HOLA, SOY UN MODELO DE LENGUAJE.”**

---

# 🧱 17 · PRINCIPIOS

<table>
<tr>
<td align="center"><b>LOCAL FIRST</b><br><sub>La experiencia no depende de la nube para existir.</sub></td>
<td align="center"><b>ONE CARD</b><br><sub>Menos elementos. Más intención.</sub></td>
<td align="center"><b>VOICE LOCAL</b><br><sub>Piper mantiene la voz en la máquina.</sub></td>
</tr>
<tr>
<td align="center"><b>PROVIDER AGNOSTIC</b><br><sub>El cerebro puede cambiar.</sub></td>
<td align="center"><b>EXPERIENCE FIRST</b><br><sub>La interfaz no explica la infraestructura.</sub></td>
<td align="center"><b>MINIMAL RULES</b><br><sub>La experiencia tiene límites deliberados.</sub></td>
</tr>
</table>

---

# 🗂 18 · ESTRUCTURA

```text
aigoritmo/
│
├── .env.example
├── .env
│
├── PROBAR-ARCANA.ps1
├── PROBAR-ARCANA.bat
├── COMO-EJECUTAR.md
│
├── backend/
│   ├── ...
│   └── ...
│
├── frontend/
│   ├── ...
│   └── ...
│
├── cards/
│   └── ...
│
└── voice/
    └── Piper/
```

La implementación puede crecer.

La ecuación no:

```text
PRESENCE
+
CARD
+
BRAIN
+
VOICE
=
EXPERIENCE
```

---

# 🧩 19 · STACK

<div align="center">

<img src="https://skillicons.dev/icons?i=python,html,css,js&theme=dark" alt="Core stack">

<br><br>

![Ollama](https://img.shields.io/badge/Ollama-LOCAL-111111?style=flat-square)
![OpenAI](https://img.shields.io/badge/OpenAI-API-412991?style=flat-square)
![xAI](https://img.shields.io/badge/xAI-Grok-000000?style=flat-square)
![Piper](https://img.shields.io/badge/Piper-LOCAL%20TTS-7DC7A8?style=flat-square)
![Pollinations](https://img.shields.io/badge/Pollinations-OPTIONAL-C9A86A?style=flat-square)

</div>

---

# 🌒 20 · AIGORITMO · ECOSYSTEM

<div align="center">

```text
                           GRACIANB
                              │
              ┌───────────────┼────────────────┐
              │               │                │
              ▼               ▼                ▼
       PROFESSIONAL         PLAY              YOGA
          DECK               LAB           INSTRUCTOR
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
                  OHANA              VÓRTICE
                                          │
                                          │
                                          ▼
                                      AIGORITMO
                                   ARCANA · ARCANO
```

</div>

### El proyecto pertenece al laboratorio **PLAY**.

Pero Aigoritmo tiene su propia identidad:

**IA · voz · interacción · presencia · experimentación local**

---

# 🕯 21 · THE FINAL CARD

<div align="center">

<br>

<img src="https://img.shields.io/badge/ARCANA-ORO_%2F_VELVET-C9A86A?style=for-the-badge&labelColor=080706">

   

<img src="https://img.shields.io/badge/ARCANO-ACERO_%2F_NOCHE-8FA6B8?style=for-the-badge&labelColor=080B10">

<br><br>

## **UNA CARTA.**

## **UNA PRESENCIA.**

## **UNA RESPUESTA.**

<br>

> ### **La tecnología desaparece.**
>
> ### **La presencia permanece.**

<br><br>

<a href="http://127.0.0.1:8000">
<img src="https://img.shields.io/badge/%E2%96%B6%20ENTRAR%20EN%20ARCANA-C9A86A?style=for-the-badge&labelColor=050505" alt="Entrar en Arcana">
</a>

</div>

---

# ◇ 22 · ECOSISTEMA

<div align="center">

<a href="https://gracianb.github.io/GracianB/">
<img src="https://img.shields.io/badge/01-HUB-C4A574?style=for-the-badge&labelColor=080808" alt="Hub">
</a>

<a href="https://gracianb.github.io/professional-deck/">
<img src="https://img.shields.io/badge/01-PROFESSIONAL%20DECK-F4F3EE?style=for-the-badge&labelColor=080808" alt="Professional deck">
</a>

<a href="https://gracianb.github.io/systems-lab/">
<img src="https://img.shields.io/badge/02-SYSTEMS%20LAB-7AF3FF?style=for-the-badge&labelColor=080808" alt="Systems lab">
</a>

<a href="https://gracianb.github.io/project-ohana/">
<img src="https://img.shields.io/badge/OHANA-CANVAS-7AF3FF?style=for-the-badge&labelColor=080808" alt="Ohana">
</a>

<a href="https://vortex-gilt-xi.vercel.app/">
<img src="https://img.shields.io/badge/VÓRTICE-WEBGL-7AF3FF?style=for-the-badge&labelColor=080808" alt="Vórtice">
</a>

<a href="https://gracianb.github.io/yoga-instructor/">
<img src="https://img.shields.io/badge/03-YOGA-7DCAA5?style=for-the-badge&labelColor=080808" alt="Yoga">
</a>

</div>

---

<div align="center">

<br><br>

<img
src="https://capsule-render.vercel.app/api?type=waving&height=180&section=footer&color=0:050505,35:21170D,70:0D0A07,100:030303&animation=twinkling"
width="100%"
alt="Aigoritmo footer"
/>

<br>

# **AIGORITMO**

### `ARCANA · ARCANO`

`LOCAL STUDIO · AI · VOICE · PRESENCE`

<br>

[![GitHub](https://img.shields.io/badge/GitHub-GracianB-181717?style=for-the-badge\&logo=github)](https://github.com/GracianB)

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Gracián%20Baena-0A66C2?style=for-the-badge\&logo=linkedin\&logoColor=white)](https://www.linkedin.com/in/gracianbaena/)

<br>

<sub>

**MIT © 2026 Gracián Baena**

<br>

`Built locally. Designed as a presence.`

</sub>

<br><br>

</div>
