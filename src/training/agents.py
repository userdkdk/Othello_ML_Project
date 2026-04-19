from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import List, Optional, Protocol, Tuple, Union

from engine.move_validator import get_flippable_positions
from engine.types import GameState, Position


Action = Union[Position, str]


class Agent(Protocol):
    name: str
    version: str

    def select_action(
        self,
        state: GameState,
        valid_moves: List[Position],
        rng: Optional[Random] = None,
    ) -> Action:
        ...


@dataclass
class RandomAgent:
    name: str = "random-agent"
    version: str = "random-v1"

    def select_action(
        self,
        state: GameState,
        valid_moves: List[Position],
        rng: Optional[Random] = None,
    ) -> Action:
        if not valid_moves:
            return "PASS"
        picker = rng or Random()
        return picker.choice(valid_moves)


@dataclass
class HeuristicAgent:
    name: str = "heuristic-agent"
    version: str = "heuristic-v1"

    def select_action(
        self,
        state: GameState,
        valid_moves: List[Position],
        rng: Optional[Random] = None,
    ) -> Action:
        if not valid_moves:
            return "PASS"

        def score(move: Position) -> Tuple[int, int, int]:
            row, col = move
            corner_bonus = 1 if (row, col) in {(0, 0), (0, 7), (7, 0), (7, 7)} else 0
            edge_bonus = 1 if row in {0, 7} or col in {0, 7} else 0
            flips = len(get_flippable_positions(state.board, state.current_player, move))
            return corner_bonus, edge_bonus, flips

        return max(valid_moves, key=score)
