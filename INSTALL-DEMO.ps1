param([switch]$Run)
$ErrorActionPreference='Stop'
$root=Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location "$root\\backend"
if(!(Test-Path .venv)){python -m venv .venv}
& .\.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel
& .\.venv\Scripts\python.exe -m pip install -e .
if($Run){& .\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000}
else{Write-Host 'Instalación completada. Ejecuta: .\\INSTALL-DEMO.ps1 -Run'}
