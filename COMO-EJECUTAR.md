# Cómo ejecutar Aigoritmo (Arcana / Arcano)

Carpeta del proyecto (GitHub): `X:\GitHub\systems-lab\aigoritmo`

Todo corre en local: `127.0.0.1`. No abras puertos a la red.

## Qué hace

- **Arcana**: habla (Piper, voz Daniela), tira **1 carta** ella y genera la imagen de la tirada. No tienes que subir fotos.
- **Arcano**: igual, con voz Gevy y su vídeo.
- El vídeo (horizontal, casi a pantalla completa) se ve **una vez** (en Arcana, antes el mago invocando el orbe). Luego queda el orbe. El chat carga al lado.

## URL principal

**http://127.0.0.1:8000** - FastAPI sirve el estudio (`frontend/dist`). Es la URL de Arcana.

Vite en **http://127.0.0.1:5173** es opcional (hot reload al editar el frontend).

## En tu PC (sin túnel)

Para usarlo tú, **no hace falta el túnel**. Solo local:

```powershell
# 1) Ollama (modelo llama3.2:3b en X:\Aigoritmo\ollama_models)
powershell -File X:\GitHub\systems-lab\aigoritmo\scripts\start-ollama.ps1

# 2) Demo: API + estudio
powershell -File X:\GitHub\systems-lab\aigoritmo\scripts\start-demo.ps1
```

Navegador **en esta máquina**:

- Estudio: **http://127.0.0.1:8000**
- Vite (opcional): http://127.0.0.1:5173
- Salud del sistema: http://127.0.0.1:8000/health

Atajo: `X:\PROBAR-ARCANA.bat`.

Pulsa **Entrar**. Un saludo no lanza cartas. Si pides una tirada o pulsas **Tirar una carta**, genera **una sola carta** del Arcano Mayor y su imagen. Nunca un abanico de tres.

Si Ollama y FastAPI ya están en marcha, basta con abrir `http://127.0.0.1:8000`. El túnel no entra en esta receta.

## Arranque a mano (si el script falla)

Terminal 1 - Ollama ya tiene que estar en `127.0.0.1:11434`.

Terminal 2 - API (sirve también el estudio si `frontend/dist` existe):

```powershell
Set-Location X:\GitHub\systems-lab\aigoritmo\backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```


## Si no habla o no carga

1. Abre http://127.0.0.1:8000/health
2. Recarga el estudio con Ctrl+F5.

Vite opcional en :5173. Tras editar el frontend, reconstruye dist para que :8000 coincida.

## Imágenes

No hace falta enviar una foto. La visión de la tirada se dibuja al instante en local; Pollinations puede sustituirla en unos 8 segundos. Subir una imagen es opcional.
