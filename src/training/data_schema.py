from __future__ import annotations

from typing import Any, Dict, Iterable, List

from training.episode import Episode


def episode_to_dict(episode: Episode) -> Dict[str, Any]:
    return episode.to_dict()


def episodes_to_dicts(episodes: Iterable[Episode]) -> List[Dict[str, Any]]:
    return [episode_to_dict(episode) for episode in episodes]
