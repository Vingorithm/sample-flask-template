<#
.SYNOPSIS
  One-shot project setup: venv (Python 3.12), dependencies, .env, Tailwind build, DB migrations.

.EXAMPLE
  .\scripts\setup.ps1          # development
  .\scripts\setup.ps1 -Prod    # production (no dev tools, APP_ENV=production in new .env)
#>
param(
    [switch]$Prod,
    [string]$PythonVersion = "3.12"
)

$ErrorActionPreference = "Stop"
$root = (Resolve-Path "$PSScriptRoot\..").Path
Set-Location $root

function Step($msg) { Write-Host "==> $msg" -ForegroundColor Cyan }

# 1. Virtual environment -------------------------------------------------
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Step "Creating .venv with Python $PythonVersion"
    if (Get-Command py -ErrorAction SilentlyContinue) {
        py "-$PythonVersion" -m venv .venv
    } else {
        python -m venv .venv
    }
    if ($LASTEXITCODE -ne 0) { throw "Could not create venv. Is Python $PythonVersion installed? (py -0p lists versions)" }
}
$py = Join-Path $root ".venv\Scripts\python.exe"

$actual = & $py -c "import sys; print('%d.%d' % sys.version_info[:2])"
if ($actual -ne $PythonVersion) {
    Write-Warning "venv uses Python $actual, project targets $PythonVersion (.python-version)."
}

# 2. Python dependencies -----------------------------------------------
$req = if ($Prod) { "requirements\prod.txt" } else { "requirements\dev.txt" }
Step "Installing $req"
& $py -m pip install --upgrade pip --quiet
& $py -m pip install -r $req
if ($LASTEXITCODE -ne 0) { throw "pip install failed" }

# 3. .env -------------------------------------------------------------
if (-not (Test-Path ".env")) {
    Step "Creating .env from .env.example"
    $secret = & $py -c "import secrets; print(secrets.token_hex(32))"
    $content = Get-Content ".env.example" -Raw
    $content = $content -replace "(?m)^SECRET_KEY=.*$", "SECRET_KEY=$secret"
    if ($Prod) {
        $content = $content -replace "(?m)^APP_ENV=.*$", "APP_ENV=production"
        $content = $content -replace "(?m)^FLASK_DEBUG=.*\r?\n", ""
    }
    [System.IO.File]::WriteAllText((Join-Path $root ".env"), $content)
    if ($Prod) { Write-Warning "Fill in DB_* (MySQL) in .env, then re-run this script." }
} else {
    Step ".env already exists, leaving it untouched"
}

# 4. Tailwind CSS ------------------------------------------------------
if (Get-Command npm -ErrorAction SilentlyContinue) {
    Step "Installing npm packages and building CSS"
    if (Test-Path "package-lock.json") { npm ci } else { npm install }
    npm run build
} else {
    Write-Warning "npm not found: install Node.js LTS, then run 'npm install; npm run build'."
}

# 5. Database --------------------------------------------------------------
Step "Applying database migrations"
& $py -m flask db upgrade
if ($LASTEXITCODE -ne 0) { Write-Warning "Migration failed. Check database settings in .env." }

Write-Host ""
Write-Host "Done." -ForegroundColor Green
if ($Prod) {
    Write-Host "Start server:  .venv\Scripts\python serve.py   (or deploy\windows\install-service.ps1)"
} else {
    Write-Host "Activate venv: .venv\Scripts\Activate.ps1"
    Write-Host "Run dev:       flask run     (and in a second terminal: npm run dev)"
}
