# Aigoritmo - Arcana (demo local)

Estudio local de avatares. La demo es **Arcana** y su gemelo **Arcano**: tarot cinematográfico en español, una sola carta, voz en local.

## Qué es

- Conversación con memoria de sesión
- **Una carta** del Arcano Mayor (nunca un abanico de tres ni pasado/presente/futuro)
- Un saludo **no** lanza tirada
- Imagen de la carta al instante (dibujo local; Pollinations puede sustituirla en unos segundos)
- Voz en esta máquina. El consultante no ve nombres de modelos

## Cómo ejecutarlo

```powershell
powershell -File X:\GitHub\systems-lab\aigoritmo\scripts\start-ollama.ps1
powershell -File X:\GitHub\systems-lab\aigoritmo\scripts\start-demo.ps1
```

Abre **http://127.0.0.1:8000** (FastAPI sirve `frontend/dist`). Vite en :5173 es opcional, para desarrollar el frontend.

Salud: http://127.0.0.1:8000/health

Atajo: `X:\PROBAR-ARCANA.bat` o el `PROBAR-ARCANA.ps1` de esta carpeta.

Detalle en `COMO-EJECUTAR.md`.

## Tarot

Arcana genera **una** carta a partir de tu pregunta. No hace falta subir fotos. Mirar una imagen tuya es opcional, no el rito.


## Mañana API — tres modos (Ollama / Grok / ChatGPT)

Sin pegar claves en el chat. Copia `.env.example` → `.env` y edita solo en disco.

1. **Ollama (local, por defecto)** — sin `XAI_API_KEY` ni `OPENAI_API_KEY` (o con claves vacías). Arcana/Arcano usan `provider: ollama`. Arranca Ollama + demo como arriba.
2. **Grok (xAI / SpaceXAI)** — en `.env`: `XAI_API_KEY=...`. Reinicia la API. Arcana/Arcano ya tienen `preferred_provider: spacexai` + `catalog_model: grok-4.5`; con la clave, el chat usa Grok. Health: `xai_ready` / `providers.spacexai.ready: true` (la clave no se muestra).
3. **ChatGPT (OpenAI)** — en `.env`: `OPENAI_API_KEY=...` y `LLM_PROVIDER=openai`. Reinicia la API. Modelo por defecto `gpt-4.1` (`OPENAI_MODEL`); barato: `OPENAI_MODEL=gpt-4o-mini`. Health: `openai_ready` / `providers.openai.ready: true`.

`LLM_PROVIDER` / `FORCE_LLM_PROVIDER` aceptan `openai` | `spacexai` | `ollama` y pisan el preferred del YAML. No hace falta poner ambas claves: con solo xAI funciona Grok; con solo OpenAI + `LLM_PROVIDER=openai` funciona ChatGPT.

Piper (voz) sigue 100% local. Pollinations (imagen) no cambia.
