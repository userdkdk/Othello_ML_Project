#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
hooks_dir="$repo_root/.git/hooks"

if [[ ! -d "$hooks_dir" ]]; then
  echo ".git/hooks not found"
  exit 1
fi

mkdir -p "$hooks_dir"
cp "$repo_root/.githooks/pre-commit" "$hooks_dir/pre-commit"
chmod +x "$hooks_dir/pre-commit"

echo "installed: .git/hooks/pre-commit"
