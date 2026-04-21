from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
META_FILES = sorted(
    path for path in (ROOT / "meta").rglob("*")
    if path.is_file() and path.suffix in {".json", ".jsonl"}
)


def read_snapshot() -> dict[str, str]:
    snapshot: dict[str, str] = {}
    for path in META_FILES:
        snapshot[path.relative_to(ROOT).as_posix()] = path.read_text(encoding="utf-8")
    return snapshot


def main() -> int:
    before = read_snapshot()
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build_meta_index.py")],
        cwd=ROOT,
        check=False,
    )
    if result.returncode != 0:
        return result.returncode

    after = read_snapshot()
    changed = [path for path in sorted(after) if before.get(path) != after.get(path)]

    if not changed:
        print("meta-check-ok")
        return 0

    print("meta-check-failed")
    print("stale files:")
    for path in changed:
        print(path)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
