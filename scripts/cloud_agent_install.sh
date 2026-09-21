#!/usr/bin/env bash
# Idempotent Cloud Agent bootstrap for the AI Image Edit project.
# Installs backend (FastAPI) + frontend (Next.js) dependencies and writes the
# local, gitignored env files the launchers expect. Safe to run repeatedly.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "==> System: ensure python venv support"
# Cursor's default image ships python3.12 without the venv/ensurepip module.
# Install it once if creating a virtualenv is not yet possible.
if ! python3 -c "import ensurepip, venv" >/dev/null 2>&1; then
  sudo apt-get update -y
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends python3-venv
fi

echo "==> Backend: Python virtualenv"
if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --upgrade pip

# No GPU in the Cloud Agent VM: install CPU-only torch/torchvision from the
# PyTorch CPU index before the rest of the requirements so pip does not pull the
# multi-GB CUDA wheels. requirements.txt keeps torch>=2.3.0, which these satisfy.
echo "==> Backend: CPU torch/torchvision"
pip install --index-url https://download.pytorch.org/whl/cpu "torch>=2.3.0" "torchvision>=0.18.0"

echo "==> Backend: requirements.txt"
pip install -r backend/requirements.txt

echo "==> Frontend: npm dependencies"
(cd frontend && npm ci)

echo "==> Local env files (gitignored)"
bash scripts/cloud_agent_write_env.sh

echo "==> Install complete"
