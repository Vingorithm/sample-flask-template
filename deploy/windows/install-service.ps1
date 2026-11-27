<#
.SYNOPSIS
  Register Waitress as a Windows service using NSSM (https://nssm.cc).

.EXAMPLE
  # Run in an elevated PowerShell from the project root:
  .\deploy\windows\install-service.ps1 -ServiceName flaskapp
#>
param(
    [string]$ServiceName = "flaskapp",
    [string]$Nssm = "nssm",
    [string]$AppRoot = (Resolve-Path "$PSScriptRoot\..\..").Path
)

$ErrorActionPreference = "Stop"

$python = Join-Path $AppRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) { throw "venv not found at $python. Run scripts\setup.ps1 -Prod first." }
if (-not (Get-Command $Nssm -ErrorAction SilentlyContinue)) { throw "nssm not found. Install it and add to PATH, or pass -Nssm <path>." }

$logDir = Join-Path $AppRoot "logs"
New-Item -ItemType Directory -Force $logDir | Out-Null

& $Nssm install $ServiceName $python "serve.py"
& $Nssm set $ServiceName AppDirectory $AppRoot
& $Nssm set $ServiceName AppEnvironmentExtra "APP_ENV=production"
& $Nssm set $ServiceName DisplayName "$ServiceName (Flask/Waitress)"
& $Nssm set $ServiceName Start SERVICE_AUTO_START
& $Nssm set $ServiceName AppStdout (Join-Path $logDir "service-stdout.log")
& $Nssm set $ServiceName AppStderr (Join-Path $logDir "service-stderr.log")
& $Nssm set $ServiceName AppRotateFiles 1
& $Nssm set $ServiceName AppRotateBytes 10485760
& $Nssm set $ServiceName AppExit Default Restart

& $Nssm start $ServiceName
Write-Host "Service '$ServiceName' installed and started." -ForegroundColor Green
