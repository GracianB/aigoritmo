$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$ollama = Join-Path $env:LOCALAPPDATA "Programs\Ollama\ollama.exe"
$py = Join-Path $root "backend\.venv\Scripts\python.exe"
$env:OLLAMA_MODELS = "X:\Aigoritmo\ollama_models"

if (Test-Path $ollama) {
  try {
    Invoke-WebRequest -Uri "http://127.0.0.1:11434/api/tags" -UseBasicParsing -TimeoutSec 1 | Out-Null
  } catch {
    Start-Process -FilePath $ollama -ArgumentList "serve" -WindowStyle Hidden
    Start-Sleep -Seconds 2
  }
}

if (-not (Test-Path $py)) { throw "Falta el venv. En backend: python -m venv .venv  y  pip install -e ." }

Start-Process -FilePath $py -ArgumentList @(
  "-m", "uvicorn", "app.main:app",
  "--host", "127.0.0.1",
  "--port", "8000"
) -WorkingDirectory (Join-Path $root "backend") -WindowStyle Hidden

if (-not (Test-Path (Join-Path $root "frontend\node_modules"))) {
  Push-Location (Join-Path $root "frontend")
  npm install
  Pop-Location
}

Write-Host "API    http://127.0.0.1:8000/health"
Write-Host "Studio http://127.0.0.1:5173"
Write-Host "Entra como invitado -> Arcana -> formula una pregunta."
Push-Location (Join-Path $root "frontend")
npm run dev
Pop-Location
