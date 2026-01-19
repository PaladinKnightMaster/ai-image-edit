#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="./models/flux2_klein_9b_gguf"
QUANT="Q4_K_M"
TEXT_ENCODER="${FLUX2_TEXT_ENCODER_PRECISION:-fp4}"
LLM_FILE="${FLUX2_LLM_FILE:-Qwen3-8B-Q6_K.gguf}"
TOKEN=""
CLEAN_CACHE=0
SKIP_LLM=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --output-dir)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    --quant)
      QUANT="$2"
      shift 2
      ;;
    --text-encoder)
      TEXT_ENCODER="$2"
      shift 2
      ;;
    --llm-file)
      LLM_FILE="$2"
      shift 2
      ;;
    --skip-llm)
      SKIP_LLM=1
      shift 1
      ;;
    --token)
      TOKEN="$2"
      shift 2
      ;;
    --clean-cache)
      CLEAN_CACHE=1
      shift 1
      ;;
    *)
      echo "Unknown arg: $1" >&2
      exit 1
      ;;
  esac
done

PYTHON_BIN="${PYTHON_BIN:-python}"

ARGS=(
  "$SCRIPT_DIR/fetch_flux2_klein_assets.py"
  --output-dir "$OUTPUT_DIR"
  --quant "$QUANT"
  --text-encoder "$TEXT_ENCODER"
  --llm-file "$LLM_FILE"
)

if [[ -n "$TOKEN" ]]; then
  ARGS+=(--token "$TOKEN")
fi
if [[ "$SKIP_LLM" -eq 1 ]]; then
  ARGS+=(--skip-llm)
fi
if [[ "$CLEAN_CACHE" -eq 1 ]]; then
  ARGS+=(--clean-cache)
fi

$PYTHON_BIN "${ARGS[@]}"
