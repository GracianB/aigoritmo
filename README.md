# Aigoritmo — Arcana · Arcano (versión definitiva)

Estudio local cinematográfico en español. **Arcana** (oro/velvet, cálida) y **Arcano** (acero/noche, grave): una sola carta del Arcano Mayor, voz Piper en esta máquina, cerebro Ollama o API (Grok / ChatGPT).

## Qué es (cerrado)

- Dos presencias terminadas, no un catálogo de avatares
- Un saludo **no** lanza tirada
- **Una carta** por consulta (nunca tres ni pasado/presente/futuro)
- Carta local al instante; Pollinations puede sustituirla en ~8s
- Voz 100% local (Piper). El consultante no ve nombres de modelos
- Chat amplio tipo salón, orbe de presencia, cambio de avatar con fundido

## Cómo ejecutarlo

```powershell
powershell -File X:\GitHub\systems-lab\aigoritmo\PROBAR-ARCANA.ps1
```

Abre **http://127.0.0.1:8000**. Salud: http://127.0.0.1:8000/health (`version`: `2.1.0-definitiva`).

Atajo: `X:\PROBAR-ARCANA.bat`. Detalle en `COMO-EJECUTAR.md`.

## LLM — Ollama / Grok / ChatGPT

Copia `.env.example` → `.env` (nunca pegues claves en el chat).

1. **Ollama** — sin `XAI_API_KEY` ni `OPENAI_API_KEY`.
2. **Grok (xAI)** — `XAI_API_KEY=...` (YAML ya prefiere `spacexai`).
3. **ChatGPT** — `OPENAI_API_KEY=...` y `LLM_PROVIDER=openai`.

`LLM_PROVIDER` acepta `openai` | `spacexai` | `ollama`. Piper y cartas no cambian.
