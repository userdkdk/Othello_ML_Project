#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

IMAGE_NAME="${IMAGE_NAME:-othello-training}"
CONTAINER_NAME="${CONTAINER_NAME:-othello-training}"

cd "$ROOT_DIR"

docker build -f Dockerfile.training -t "$IMAGE_NAME" .

mkdir -p "$ROOT_DIR/checkpoints" "$ROOT_DIR/runs"

if [ "$#" -eq 0 ]; then
  set -- pytest tests/unit/training -q
fi

docker run --rm \
  --name "$CONTAINER_NAME" \
  -v "$ROOT_DIR/checkpoints:/app/checkpoints" \
  -v "$ROOT_DIR/runs:/app/runs" \
  "$IMAGE_NAME" "$@"
