from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class MatchStatistics:
    total_games: int = 0
    black_wins: int = 0
    white_wins: int = 0
    draws: int = 0
    total_moves: int = 0
    passes: int = 0

    def record_result(self, winner: Optional[str], move_count: int, pass_count: int) -> None:
        self.total_games += 1
        self.total_moves += move_count
        self.passes += pass_count
        if winner == "BLACK":
            self.black_wins += 1
        elif winner == "WHITE":
            self.white_wins += 1
        else:
            self.draws += 1

    def to_dict(self) -> Dict[str, float]:
        average_moves = self.total_moves / self.total_games if self.total_games else 0.0
        return {
            "total_games": self.total_games,
            "black_wins": self.black_wins,
            "white_wins": self.white_wins,
            "draws": self.draws,
            "passes": self.passes,
            "average_moves": average_moves,
        }
