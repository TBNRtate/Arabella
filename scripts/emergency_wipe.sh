#!/usr/bin/env bash
set -euo pipefail

TARGET=${1:-""}

case "$TARGET" in
  vad)
    echo "Wiping VAD history..."
    rm -f data/vad_history.sqlite
    ;;
  letta)
    echo "Wiping Letta archival memory..."
    rm -f data/letta.db
    ;;
  all)
    echo "Wiping all core memory data..."
    rm -rf data/*
    ;;
  *)
    echo "Usage: $0 {vad|letta|all}" >&2
    exit 1
    ;;
esac
