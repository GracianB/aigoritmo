$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$cf = Join-Path $PSScriptRoot "cloudflared.exe"
$dist = Join-Path $root "frontend\dist\index.html"

if (-not (Test-Path $dist)) {
  Write-Host "Construyendo el estudio..."
  Push-Location (Join-Path $root "frontend")
  npm run build
  Pop-Location
}

try {
  Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -UseBasicParsing -TimeoutSec 3 | Out-Null
} catch {
  throw "Arranca primero FastAPI en 127.0.0.1:8000 (python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000)"
}

if (-not (Test-Path $cf)) {
  Write-Host "Descargando Cloudflare Tunnel..."
  curl.exe -L --fail -o $cf "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
}

Write-Host ""
Write-Host "Tu PC sigue en 127.0.0.1. El tunel da una URL https publica."
Write-Host "Cualquiera con el enlace usara TU Ollama y TU Piper. CTRL+C para cortarlo."
Write-Host ""
& $cf tunnel --url http://127.0.0.1:8000 --no-autoupdate
