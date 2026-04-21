#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

IMAGE_NAME="${IMAGE_NAME:-othello-runtime}"
CONTAINER_NAME="${CONTAINER_NAME:-othello-runtime}"
HOST_PORT="${HOST_PORT:-8000}"

cd "$ROOT_DIR"

docker build -t "$IMAGE_NAME" .

docker run --rm \
  --name "$CONTAINER_NAME" \
  -p "$HOST_PORT":8000 \
  "$IMAGE_NAME"
