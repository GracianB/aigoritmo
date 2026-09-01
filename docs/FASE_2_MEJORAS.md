# FASE 2 · HARDENING DE DEMO

## Problemas corregidos
- CORS explícito para Live Server `127.0.0.1:5500` y `localhost:5500`.
- Preflight OPTIONS cubierto por CORSMiddleware.
- Rutas de proyecto corregidas en `backend/app/main.py`.
- `/avatars` servido directamente por FastAPI.
- Nuevo endpoint `GET /api/avatar-assets/{persona_id}`.
- El frontend ya no intenta cargar rutas relativas inexistentes.
- Descubrimiento dinámico de vídeo/imagen del avatar.
- Fallback visual integrado cuando no existe ningún asset.
- Timeout de peticiones para evitar UI congelada.

## Prueba rápida
Backend:
```powershell
cd X:\GitHub\systems-lab\aigoritmo\backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Comprobar CORS:
```powershell
curl.exe -i -X OPTIONS "http://127.0.0.1:8000/api/chat" -H "Origin: http://127.0.0.1:5500" -H "Access-Control-Request-Method: POST"
```
Debe aparecer `access-control-allow-origin: http://127.0.0.1:5500`.

Frontend:
```powershell
cd X:\GitHub\systems-lab\aigoritmo
python -m http.server 5500
```
Abrir `http://127.0.0.1:5500/frontend/`.
