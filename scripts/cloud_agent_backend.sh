#!/usr/bin/env bash
# Starts the FastAPI backend for Cloud Agent (Linux equivalent of
# scripts/start_backend.ps1 -Mode main). Uses the repo virtualenv and the
# main .env profile.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# shellcheck disable=SC1091
source .venv/bin/activate

export DOTENV_PATH="$REPO_ROOT/backend/.env"

cd backend
exec python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
