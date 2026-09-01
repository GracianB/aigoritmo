# AIGORITMO · Bruno / GuruSup Demo

## The opening sentence

> "No quería enseñarte otro chatbot. Quería enseñarte qué ocurre cuando una IA tiene una identidad especializada, memoria de contexto y una arquitectura separada del modelo que la ejecuta."

## 4-minute flow

### 1. Identity
Ask ARCANA:

> ¿Quién eres y qué te diferencia de un chatbot generalista?

Point out that the persona is not hard-coded into the frontend. It lives in a persona layer.

### 2. Specialization
Run a three-card spread.

Explain that the application generates structured context and stores the spread in the active conversation.

### 3. Memory
Ask:

> Relaciona mi pregunta anterior con la carta que apareció en el presente.

This demonstrates continuity rather than isolated prompt-response behavior.

### 4. Architecture
Show:

- `/api/avatars`
- `/health`
- `/ready`
- `/docs`

Then explain: **ARCANA is only Enigma, the demonstration avatar.** The architecture can register different identities and specialties over the same conversation engine.

## Strongest technical points

- Local-first inference with Ollama
- Provider abstraction
- Persona registry
- Bounded contextual memory
- Specialized workflows
- Multimodal endpoint
- Media-enabled demo layer
- API-first architecture
- GitHub reproducibility

## Avoid saying

- "I made a tarot chatbot"
- "It's basically ChatGPT with a prompt"

## Say instead

> "ARCANA is a constrained demonstration identity used to prove a reusable architecture for specialized conversational avatars."
