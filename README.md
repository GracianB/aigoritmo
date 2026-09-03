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
