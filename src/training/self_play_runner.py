from __future__ import annotations

from dataclasses import dataclass
from typing import List

from training.agents import Agent
from training.episode import Episode
from training.match_runner import MatchResult, run_match
from training.statistics import MatchStatistics


@dataclass
class SelfPlayResult:
    episodes: List[Episode]
    statistics: MatchStatistics
    failures: int


def run_self_play(
    black_agent: Agent,
    white_agent: Agent,
    num_games: int,
    seed: int = 0,
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
            continue
        statistics.record_result(
            winner=result.episode.winner,
            move_count=result.move_count,
            pass_count=result.pass_count,
        )

    return SelfPlayResult(
        episodes=episodes,
        statistics=statistics,
        failures=failures,
    )
