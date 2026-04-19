from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from training.agents import Agent
from training.self_play_runner import run_self_play


@dataclass
class EvaluationReport:
    games: int
    black_win_rate: float
    white_win_rate: float
    draw_rate: float
    failures: int


class Evaluator:
    def evaluate(
        self,
        black_agent: Agent,
        white_agent: Agent,
        num_games: int,
        seed: int = 0,
    ) -> EvaluationReport:
        result = run_self_play(
            black_agent=black_agent,
            white_agent=white_agent,
            num_games=num_games,
            seed=seed,
        )
        stats = result.statistics
        total = stats.total_games or 1
        return EvaluationReport(
            games=stats.total_games,
            black_win_rate=stats.black_wins / total,
            white_win_rate=stats.white_wins / total,
            draw_rate=stats.draws / total,
            failures=result.failures,
        )
