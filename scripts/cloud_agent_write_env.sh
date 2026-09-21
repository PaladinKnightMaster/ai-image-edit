#!/usr/bin/env bash
# Writes the local, gitignored env files the backend launchers and tests expect.
# Only creates a file if it does not already exist, so user edits are preserved.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

write_if_missing() {
  local path="$1"
  if [ -f "$path" ]; then
    echo "    keep   $path (already exists)"
  else
    cat > "$path"
    echo "    create $path"
  fi
}

# Main development profile. Offline mode, CPU-friendly quality profile, all
# models enabled (they report present=false until mirrored locally).
write_if_missing backend/.env <<'ENV'
APP_NAME=ai-image-edit
APP_VERSION=0.1.0
APP_COMMIT=dev
FRONTEND_ORIGIN=http://localhost:3000
OFFLINE_MODE=1
QUALITY_PROFILE=cpu-low
WARMUP_MODELS=1
DB_PATH=./data/app.db
ENV

# Fast-check profile used by scripts/smoke_backend.ps1 and
# backend/tests/test_startup_smoke.py. Must keep these exact values.
write_if_missing backend/.env.fast-check <<'ENV'
APP_NAME=ai-image-edit
APP_VERSION=0.1.0
APP_COMMIT=dev
FRONTEND_ORIGIN=http://localhost:3000
OFFLINE_MODE=1
INFERENCE_MODE=local
QUALITY_PROFILE=cpu-low
WARMUP_MODELS=1
DB_PATH=./data/app.fast-check.db
ENABLED_MODELS=qwen-image-2512
ENV

# Frontend points at the local backend.
write_if_missing frontend/.env.local <<'ENV'
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
ENV
