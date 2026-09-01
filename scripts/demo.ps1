$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$ollamaModels = "X:\Aigoritmo\ollama_models"
$ollamaExe = "C:\Users\graci\AppData\Local\Programs\Ollama\ollama.exe"
$py = Join-Path $root "backend\.venv\Scripts\python.exe"
$vite = Join-Path $root "frontend\node_modules\vite\bin\vite.js"

function Test-Listen([int]$Port) {
  try {
    $client = New-Object System.Net.Sockets.TcpClient
    $iar = $client.BeginConnect("127.0.0.1", $Port, $null, $null)
    $ok = $iar.AsyncWaitHandle.WaitOne(400)
    if ($ok) { $client.EndConnect($iar) }
    $client.Close()
    return $ok
  } catch {
    return $false
  }
}

New-Item -ItemType Directory -Force -Path $ollamaModels | Out-Null
[Environment]::SetEnvironmentVariable("OLLAMA_MODELS", $ollamaModels, "User")
[Environment]::SetEnvironmentVariable("OLLAMA_HOST", "127.0.0.1:11434", "User")
[Environment]::SetEnvironmentVariable("OLLAMA_VULKAN", "false", "User")
[Environment]::SetEnvironmentVariable("OLLAMA_LLM_LIBRARY", "cpu", "User")
$env:OLLAMA_MODELS = $ollamaModels
$env:OLLAMA_HOST = "127.0.0.1:11434"
$env:OLLAMA_VULKAN = "false"
$env:OLLAMA_LLM_LIBRARY = "cpu"

if (-not (Test-Path $ollamaExe)) { Write-Error "Falta $ollamaExe" }
function Start-OllamaServe {
  Write-Host "Arrancando ollama serve (CPU, OLLAMA_MODELS=$ollamaModels)..."
  Get-Process -Name "ollama app","ollama" -ErrorAction SilentlyContinue | Stop-Process -Force
  Start-Sleep -Seconds 1
  Start-Process -FilePath $ollamaExe -ArgumentList "serve" -WindowStyle Hidden
  $deadline = (Get-Date).AddSeconds(25)
  while (-not (Test-Listen 11434)) {
    if ((Get-Date) -gt $deadline) { Write-Error "Ollama no abrio 127.0.0.1:11434" }
    Start-Sleep -Milliseconds 400
  }
}

if (-not (Test-Listen 11434)) {
  Start-OllamaServe
}

Write-Host "Calentando llama3.2:3b (primera carga)..."
$warmupFile = Join-Path $env:TEMP "aigoritmo-ollama-warmup.json"
Set-Content -Path $warmupFile -Value '{"model":"llama3.2:3b","prompt":"ok","stream":false,"keep_alive":"30m","options":{"num_predict":1,"num_ctx":1024}}' -Encoding ascii
$warmupOut = & curl.exe -sS -m 180 http://127.0.0.1:11434/api/generate -H "Content-Type: application/json" --data-binary "@$warmupFile"
if ($warmupOut -match "0xc0000005|llama-server process has terminated") {
  Write-Host "Vulkan/GPU crash detectado. Reinicio de Ollama en CPU..."
  Start-OllamaServe
  $warmupOut = & curl.exe -sS -m 180 http://127.0.0.1:11434/api/generate -H "Content-Type: application/json" --data-binary "@$warmupFile"
}
if ($warmupOut -match '"error"') {
  Write-Host "Aviso: warmup de Ollama no completo. El primer chat puede tardar."
}

if (-not (Test-Path $py)) {
  Write-Host "Creando venv del backend..."
  $sysPy = "C:\Users\graci\AppData\Local\Programs\Python\Python312\python.exe"
  if (-not (Test-Path $sysPy)) { $sysPy = "py" }
  if ($sysPy -eq "py") { py -3.12 -m venv (Join-Path $root "backend\.venv") } else { & $sysPy -m venv (Join-Path $root "backend\.venv") }
}
Push-Location (Join-Path $root "backend")
& $py -m pip install -e . --quiet
Pop-Location

if (-not (Test-Path $vite)) {
  Push-Location (Join-Path $root "frontend")
  npm install
  Pop-Location
}

if (-not (Test-Listen 8000)) {
  Write-Host "Arrancando FastAPI en 127.0.0.1:8000..."
  Start-Process -FilePath $py -ArgumentList @(
    "-m", "uvicorn", "app.main:app",
    "--app-dir", (Join-Path $root "backend"),
    "--host", "127.0.0.1",
    "--port", "8000"
  ) -WorkingDirectory (Join-Path $root "backend") -WindowStyle Hidden
  $deadline = (Get-Date).AddSeconds(25)
  while (-not (Test-Listen 8000)) {
    if ((Get-Date) -gt $deadline) { Write-Error "FastAPI no abrio 127.0.0.1:8000" }
    Start-Sleep -Milliseconds 400
  }
} else {
  Write-Host "FastAPI ya escucha en 127.0.0.1:8000"
}

if (-not (Test-Listen 5173)) {
  Write-Host "Arrancando Vite en 127.0.0.1:5173..."
  $npm = (Get-Command npm.cmd -ErrorAction Stop).Source
  Start-Process -FilePath $npm -ArgumentList @("run", "dev", "--", "--host", "127.0.0.1", "--port", "5173") -WorkingDirectory (Join-Path $root "frontend") -WindowStyle Hidden
  $deadline = (Get-Date).AddSeconds(25)
  while (-not (Test-Listen 5173)) {
    if ((Get-Date) -gt $deadline) { Write-Error "Vite no abrio 127.0.0.1:5173" }
    Start-Sleep -Milliseconds 400
  }
} else {
  Write-Host "Vite ya escucha en 127.0.0.1:5173"
}

Write-Host ""
Write-Host "Studio:  http://127.0.0.1:5173"
Write-Host "API:     http://127.0.0.1:8000/health"
Write-Host "Ollama:  http://127.0.0.1:11434/api/tags"
Write-Host "Models:  $ollamaModels"
