# Cómo ejecutar Aigoritmo (Arcana / Arcano)

Carpeta del proyecto (GitHub): `X:\GitHub\systems-lab\aigoritmo`

Todo corre en local: `127.0.0.1`. No abras puertos a la red.

## Qué hace

- **Arcana**: habla (Piper, voz Daniela), tira **1 carta** ella y genera la imagen de la tirada. No tienes que subir fotos.
- **Arcano**: igual, con voz Gevy y su vídeo.
- El vídeo (horizontal, casi a pantalla completa) se ve **una vez** (en Arcana, antes el mago invocando el orbe). Luego queda el orbe. El chat carga al lado.

## En tu PC (sin túnel)

Para usarlo tú, **no hace falta el túnel**. Solo local:

```powershell
# 1) Ollama (modelo llama3.2:3b en X:\Aigoritmo\ollama_models)
powershell -File X:\GitHub\systems-lab\aigoritmo\scripts\start-ollama.ps1

# 2) Demo: API + estudio
powershell -File X:\GitHub\systems-lab\aigoritmo\scripts\start-demo.ps1
```

Navegador **en esta máquina**:

- Estudio: http://127.0.0.1:5173
- Salud del sistema: http://127.0.0.1:8000/health

Pulsa **Entrar**. Un saludo no lanza cartas. Si pides una tirada —o pulsas **Tirar una carta**— genera **una sola carta** del Arcano Mayor y su imagen. Nunca un abanico de tres.

Si Ollama y FastAPI ya están en marcha, basta con abrir `http://127.0.0.1:5173`. El túnel no entra en esta receta.

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

## Enseñar a alguien de fuera (túnel)

**Tú en local: no arranques esto.** El túnel solo hace falta si otra persona, en otro sitio, tiene que abrir Arcana en su navegador.

Ollama y Piper siguen en TU PC. El túnel da una URL `https://….trycloudflare.com` sin abrir `0.0.0.0`.

1. Primero deja el local funcionando: FastAPI en `127.0.0.1:8000` (y Ollama).
2. En otra terminal:

```powershell
powershell -File X:\GitHub\systems-lab\aigoritmo\scripts\start-share.ps1
```

3. Copia la URL `https://….trycloudflare.com` y envíasela.
4. CTRL+C en esa ventana corta el acceso. Si apagas el PC o cierras FastAPI, el enlace deja de ir.

Tu navegador sigue usando `http://127.0.0.1:5173`. El enlace del túnel es para los demás.

## Imágenes

No hace falta enviar una foto. La visión de la tirada se genera sola (Pollinations; si falla, se dibuja en local). Subir una imagen es opcional.
