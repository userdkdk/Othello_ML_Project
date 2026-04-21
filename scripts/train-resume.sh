#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

OUTPUT_DIR="${OUTPUT_DIR:-/app/runs/latest}"
CHECKPOINT_NAME="${CHECKPOINT_NAME:-latest-training.pt}"
RESUME_CHECKPOINT="${RESUME_CHECKPOINT:-/app/checkpoints/${CHECKPOINT_NAME}}"
NUM_GAMES="${NUM_GAMES:-64}"
SELF_PLAY_SEED="${SELF_PLAY_SEED:-42}"
EPOCHS="${EPOCHS:-5}"
LEARNING_RATE="${LEARNING_RATE:-1e-3}"
BLACK_AGENT="${BLACK_AGENT:-random}"
WHITE_AGENT="${WHITE_AGENT:-heuristic}"
CHECKPOINT_VERSION="${CHECKPOINT_VERSION:-cnn-v1}"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --num-games)
      NUM_GAMES="$2"
      shift 2
      ;;
    --epochs)
      EPOCHS="$2"
      shift 2
      ;;
    --learning-rate)
      LEARNING_RATE="$2"
      shift 2
      ;;
    --checkpoint-name)
      CHECKPOINT_NAME="$2"
      RESUME_CHECKPOINT="/app/checkpoints/${CHECKPOINT_NAME}"
      shift 2
      ;;
    --output-dir)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    --resume-checkpoint)
      RESUME_CHECKPOINT="$2"
      shift 2
      ;;
    --black-agent)
      BLACK_AGENT="$2"
      shift 2
      ;;
    --white-agent)
      WHITE_AGENT="$2"
      shift 2
      ;;
    --self-play-seed)
      SELF_PLAY_SEED="$2"
      shift 2
      ;;
    --checkpoint-version)
      CHECKPOINT_VERSION="$2"
      shift 2
      ;;
    *)
      echo "unsupported option: $1" >&2
      echo "usage: ./scripts/train-resume.sh [--num-games N] [--epochs N] [--learning-rate V] [--checkpoint-name NAME] [--output-dir DIR] [--resume-checkpoint PATH]" >&2
      exit 1
      ;;
  esac
done

ARGS=(
  python
  scripts/train_policy.py
  --output-dir "$OUTPUT_DIR"
  --num-games "$NUM_GAMES"
  --self-play-seed "$SELF_PLAY_SEED"
  --epochs "$EPOCHS"
  --learning-rate "$LEARNING_RATE"
  --black-agent "$BLACK_AGENT"
  --white-agent "$WHITE_AGENT"
  --checkpoint-name "$CHECKPOINT_NAME"
  --checkpoint-version "$CHECKPOINT_VERSION"
)

if [ -f "$ROOT_DIR/checkpoints/${CHECKPOINT_NAME}" ]; then
  ARGS+=(--resume-from "$RESUME_CHECKPOINT")
fi

"$ROOT_DIR/scripts/run-training.sh" "${ARGS[@]}"
