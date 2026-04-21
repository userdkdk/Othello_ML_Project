from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from training.agents import Agent
from training.episode import Episode
from training.match_runner import MatchResult, run_match
from training.statistics import MatchStatistics


@dataclass
class SelfPlayResult:
    episodes: List[Episode]
    statistics: MatchStatistics
    failures: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "episodes": [episode.to_dict() for episode in self.episodes],
            "statistics": self.statistics.to_dict(),
            "failures": self.failures,
        }


def run_self_play(
    black_agent: Agent,
    white_agent: Agent,
    num_games: int,
    seed: int = 0,
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> SelfPlayResult:
    episodes: List[Episode] = []
    statistics = MatchStatistics()
    failures = 0

    for game_index in range(num_games):
        result: MatchResult = run_match(
            black_agent=black_agent,
            white_agent=white_agent,
            seed=seed + game_index,
            episode_id=f"episode-{game_index:06d}",
        )
        episodes.append(result.episode)
        if result.episode.status == "failed":
            failures += 1
            if progress_callback is not None:
                progress_callback(game_index + 1, num_games)
            continue
        statistics.record_result(
            winner=result.episode.winner,
            move_count=result.move_count,
            pass_count=result.pass_count,
        )
        if progress_callback is not None:
            progress_callback(game_index + 1, num_games)

    return SelfPlayResult(
        episodes=episodes,
        statistics=statistics,
        failures=failures,
    )
