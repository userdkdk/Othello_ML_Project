from __future__ import annotations

import json
from dataclasses import dataclass
from os import PathLike
from typing import Any, Iterable, Mapping, Union

from training.episode import Episode


EpisodeLike = Union[Episode, Mapping[str, Any]]


@dataclass
class EpisodeWriteError(Exception):
    message: str
    written_count: int

    def __str__(self) -> str:
        return self.message


def write_episodes_jsonl(
    path: str | PathLike[str],
    episodes: Iterable[EpisodeLike],
    mode: str = "w",
) -> int:
    if mode not in {"w", "a"}:
        raise ValueError(f"unsupported file mode: {mode}")

    written_count = 0
    try:
        with open(path, mode, encoding="utf-8") as handle:
            for episode in episodes:
                payload = _normalize_episode(episode)
                handle.write(json.dumps(payload, ensure_ascii=False))
                handle.write("\n")
                written_count += 1
    except Exception as exc:  # pragma: no cover - exercised by tests via concrete exception types
        raise EpisodeWriteError(
            message=f"failed to write episodes jsonl: {exc}",
            written_count=written_count,
        ) from exc

    return written_count


def _normalize_episode(episode: EpisodeLike) -> Mapping[str, Any]:
    if isinstance(episode, Episode):
        return episode.to_dict()
    if isinstance(episode, Mapping):
        return episode
    raise TypeError(f"unsupported episode payload type: {type(episode)!r}")
