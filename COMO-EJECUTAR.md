# Cómo ejecutar Aigoritmo (Arcana / Arcano)

Carpeta del proyecto (GitHub): `X:\GitHub\systems-lab\aigoritmo`

Todo corre en local: `127.0.0.1`. No abras puertos a la red.

## Qué hace

- **Arcana**: habla (Piper, voz Daniela), tira 3 cartas **ella** y genera la imagen de la tirada. No tienes que subir fotos.
- **Arcano**: igual, con voz Gevy y su vídeo.
- El vídeo de Arcana se ve **una vez** (antes, el mago invocando el orbe). Luego queda el orbe.

## Arranque rápido

Abre PowerShell:

```powershell
# 1) Ollama (modelo llama3.2:3b en X:\Aigoritmo\ollama_models)
powershell -File X:\GitHub\systems-lab\aigoritmo\scripts\start-ollama.ps1

# 2) Demo: API + estudio
powershell -File X:\GitHub\systems-lab\aigoritmo\scripts\start-demo.ps1
```

Navegador:

- Estudio: http://127.0.0.1:5173
- Salud del sistema: http://127.0.0.1:8000/health

Pulsa **Entrar**. Si pide una tirada, di que sí o pulsa **Lanza la tirada**: ella genera las cartas y la imagen.

## Arranque a mano (si el script falla)

Terminal 1 — Ollama ya tiene que estar en `127.0.0.1:11434`.

Terminal 2 — API:

```powershell
Set-Location X:\GitHub\systems-lab\aigoritmo\backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Terminal 3 — interfaz:

```powershell
Set-Location X:\GitHub\systems-lab\aigoritmo\frontend
npm run dev
```

## Si no habla o no carga

1. `http://127.0.0.1:8000/health` debe decir `ollama: true` y `piper_executable: true`.
2. Recarga el estudio con **Ctrl+F5**.
3. Piper está en `X:\Aigoritmo\piper`. Modelos de chat en `X:\Aigoritmo\ollama_models`.

## Imágenes

No hace falta enviar una foto. La visión de la tirada se genera sola (Pollinations; si falla, se dibuja en local). Subir una imagen es opcional.
