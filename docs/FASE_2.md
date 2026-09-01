# AIGORITMO · FASE 2

## Implementado

- Frontend premium para la demo.
- Panel visual de ARCANA.
- Estados del avatar: idle, thinking, talking, listening, error.
- Chat conectado a `POST /api/chat`.
- Persistencia del `conversation_id` en memoria del navegador.
- Indicador de interpretación.
- Render progresivo de respuestas.
- Sugerencias de conversación.
- Métricas de sesión.
- Health check visual.
- Estado del modelo.
- Web Speech API opcional.
- Responsive layout.
- Sistema de eventos `aigoritmo:avatar`.

## Ejecución

Backend:

```powershell
cd X:\GitHub\systems-lab\aigoritmo\backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend:

Abrir `frontend/index.html` mediante un servidor estático.

Ejemplo:

```powershell
cd X:\GitHub\systems-lab\aigoritmo
python -m http.server 5500
```

Después abrir:

`http://127.0.0.1:5500/frontend/`

## Nota sobre avatar

La interfaz busca:

- `avatars/arcana/idle.mp4`
- `avatars/arcana/avatar.png`

Si el vídeo no existe o no carga, utiliza automáticamente la imagen.

La arquitectura queda preparada para añadir `thinking.mp4`, `talking.mp4` e `intro.mp4` en la siguiente iteración.
