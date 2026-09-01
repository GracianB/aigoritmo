$ErrorActionPreference = "Stop"
$ollamaModels = "X:\Aigoritmo\ollama_models"
$ollamaExe = "C:\Users\graci\AppData\Local\Programs\Ollama\ollama.exe"

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

if (-not (Test-Path $ollamaExe)) {
  Write-Error "No encuentro ollama.exe en $ollamaExe"
}

if (Test-Listen 11434) {
  Write-Host "Reiniciando Ollama en CPU con OLLAMA_MODELS=$ollamaModels"
}
Get-Process -Name "ollama app","ollama" -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 1
Write-Host "Arrancando ollama serve con OLLAMA_MODELS=$ollamaModels"
Start-Process -FilePath $ollamaExe -ArgumentList "serve" -WindowStyle Hidden
$deadline = (Get-Date).AddSeconds(20)
while (-not (Test-Listen 11434)) {
  if ((Get-Date) -gt $deadline) { Write-Error "Ollama no abrio 127.0.0.1:11434" }
  Start-Sleep -Milliseconds 400
}

& $ollamaExe list
exit $LASTEXITCODE
