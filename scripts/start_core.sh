#!/usr/bin/env bash
set -euo pipefail

if [[ ! -f .env ]]; then
  echo "Missing .env. Copy .env.example first." >&2
  exit 1
fi

source .env

if [[ -d .venv ]]; then
  source .venv/bin/activate
fi

export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0,1}"

echo "Starting Arabella core..."
python -m src.core.main
