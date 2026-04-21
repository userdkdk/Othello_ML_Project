from __future__ import annotations

from dataclasses import dataclass, field
from random import Random
from typing import Any, List, Optional, Protocol, Tuple, Union

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


@dataclass
class CNNPolicyAgent:
    model: Any
    version: str = "cnn-v1"
    name: str = "cnn-policy-agent"
    device: str = "cpu"
    policy_client: Any = field(init=False)

    def __post_init__(self) -> None:
        from training.policy_client import PolicyClient

        self.policy_client = PolicyClient(
            model=self.model,
            model_version=self.version,
            device=self.device,
        )

    def select_action(
        self,
        state: GameState,
        valid_moves: List[Position],
        rng: Optional[Random] = None,
    ) -> Action:
        return self.policy_client.predict(state, valid_moves, rng).selected_action
