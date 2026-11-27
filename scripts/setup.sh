#!/usr/bin/env bash
# One-shot project setup: venv (Python 3.12), dependencies, .env, Tailwind build, DB migrations.
#   ./scripts/setup.sh          # development
#   ./scripts/setup.sh --prod   # production
set -euo pipefail

cd "$(dirname "$0")/.."
PROD=0
[[ "${1:-}" == "--prod" ]] && PROD=1
PYTHON_VERSION="3.12"
PYTHON_BIN="${PYTHON_BIN:-python${PYTHON_VERSION}}"

step() { printf '\033[36m==> %s\033[0m\n' "$1"; }

# 1. Virtual environment
if [[ ! -x .venv/bin/python ]]; then
  step "Creating .venv with ${PYTHON_BIN}"
  "${PYTHON_BIN}" -m venv .venv
fi
PY=.venv/bin/python

actual="$($PY -c 'import sys; print("%d.%d" % sys.version_info[:2])')"
[[ "$actual" != "$PYTHON_VERSION" ]] && echo "WARNING: venv uses Python $actual, project targets $PYTHON_VERSION"

# 2. Python dependencies
REQ=requirements/dev.txt
[[ $PROD -eq 1 ]] && REQ=requirements/prod.txt
step "Installing $REQ"
$PY -m pip install --upgrade pip --quiet
$PY -m pip install -r "$REQ"

# 3. .env
if [[ ! -f .env ]]; then
  step "Creating .env from .env.example"
  secret="$($PY -c 'import secrets; print(secrets.token_hex(32))')"
  sed "s/^SECRET_KEY=.*/SECRET_KEY=${secret}/" .env.example > .env
  if [[ $PROD -eq 1 ]]; then
    sed -i 's/^APP_ENV=.*/APP_ENV=production/; /^FLASK_DEBUG=/d' .env
    echo "WARNING: fill in DB_* (MySQL) in .env, then re-run this script."
  fi
  chmod 600 .env
else
  step ".env already exists, leaving it untouched"
fi

# 4. Tailwind CSS
if command -v npm >/dev/null; then
  step "Installing npm packages and building CSS"
  if [[ -f package-lock.json ]]; then npm ci; else npm install; fi
  npm run build
else
  echo "WARNING: npm not found: install Node.js LTS, then run 'npm install && npm run build'."
fi

# 5. Database
step "Applying database migrations"
$PY -m flask db upgrade || echo "WARNING: migration failed. Check database settings in .env."

echo
echo "Done."
if [[ $PROD -eq 1 ]]; then
  echo "Start server: .venv/bin/python serve.py   (or install deploy/linux/flaskapp.service)"
else
  echo "Activate venv: source .venv/bin/activate"
  echo "Run dev:       flask run   (and in a second terminal: npm run dev)"
fi
