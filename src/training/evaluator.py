from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from training.agents import Agent
from training.self_play_runner import run_self_play


@dataclass
class EvaluationReport:
    games: int
    black_win_rate: float
    white_win_rate: float
    draw_rate: float
    failures: int
    black_side_win_rate: Optional[float] = None
    white_side_win_rate: Optional[float] = None
    balanced_eval_score: Optional[float] = None
    candidate_black_games: int = 0
    candidate_white_games: int = 0

    def to_dict(self) -> Dict[str, float]:
        payload: Dict[str, float] = {
            "games": self.games,
            "black_win_rate": self.black_win_rate,
            "white_win_rate": self.white_win_rate,
            "draw_rate": self.draw_rate,
            "failures": self.failures,
            "candidate_black_games": self.candidate_black_games,
            "candidate_white_games": self.candidate_white_games,
        }
        if self.black_side_win_rate is not None:
            payload["black_side_win_rate"] = self.black_side_win_rate
        if self.white_side_win_rate is not None:
            payload["white_side_win_rate"] = self.white_side_win_rate
        if self.balanced_eval_score is not None:
            payload["balanced_eval_score"] = self.balanced_eval_score
        return payload


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
        return _build_report_from_result(result)

    def compare_agents(
        self,
        candidate_agent: Agent,
        opponent_agent: Agent,
        *,
        num_games_per_side: int,
        seed: int = 0,
    ) -> EvaluationReport:
        candidate_as_black = self.evaluate(
            black_agent=candidate_agent,
            white_agent=opponent_agent,
            num_games=num_games_per_side,
            seed=seed,
        )
        candidate_as_white = self.evaluate(
            black_agent=opponent_agent,
            white_agent=candidate_agent,
            num_games=num_games_per_side,
            seed=seed + num_games_per_side,
        )

        black_games = candidate_as_black.games
        white_games = candidate_as_white.games
        total_games = black_games + white_games
        total_failures = candidate_as_black.failures + candidate_as_white.failures
        black_wins = (candidate_as_black.black_win_rate * black_games) + (
            candidate_as_white.black_win_rate * white_games
        )
        white_wins = (candidate_as_black.white_win_rate * black_games) + (
            candidate_as_white.white_win_rate * white_games
        )
        draws = (candidate_as_black.draw_rate * black_games) + (
            candidate_as_white.draw_rate * white_games
        )
        black_side_win_rate = candidate_as_black.black_win_rate
        white_side_win_rate = candidate_as_white.white_win_rate
        balanced_eval_score = _compute_balanced_eval_score(
            black_side_win_rate=black_side_win_rate,
            white_side_win_rate=white_side_win_rate,
            black_games=black_games,
            white_games=white_games,
        )

        divisor = total_games or 1
        return EvaluationReport(
            games=total_games,
            black_win_rate=black_wins / divisor,
            white_win_rate=white_wins / divisor,
            draw_rate=draws / divisor,
            failures=total_failures,
            black_side_win_rate=black_side_win_rate,
            white_side_win_rate=white_side_win_rate,
            balanced_eval_score=balanced_eval_score,
            candidate_black_games=black_games,
            candidate_white_games=white_games,
        )


def _build_report_from_result(result: object) -> EvaluationReport:
    stats = result.statistics
    total = stats.total_games or 1
    return EvaluationReport(
            games=stats.total_games,
            black_win_rate=stats.black_wins / total,
            white_win_rate=stats.white_wins / total,
            draw_rate=stats.draws / total,
            failures=result.failures,
        )


def _compute_balanced_eval_score(
    *,
    black_side_win_rate: float,
    white_side_win_rate: float,
    black_games: int,
    white_games: int,
) -> float:
    total_games = black_games + white_games
    if total_games == 0:
        return 0.0
    if black_games == white_games:
        return (black_side_win_rate + white_side_win_rate) / 2.0
    return ((black_side_win_rate * black_games) + (white_side_win_rate * white_games)) / total_games
