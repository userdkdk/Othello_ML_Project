from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import List, Optional, Union

from engine.types import GameState, Position
from training.action_mask import build_action_mask
from training.agents import Agent, RandomAgent


@dataclass
class PolicyOutput:
    distribution_type: str
    action_probabilities: dict[str, float]
    selected_action: Union[Position, str]
    state_value: Optional[float] = None


class PolicyClient:
    def __init__(self, agent: Optional[Agent] = None) -> None:
        self.agent = agent or RandomAgent()

    def predict(
        self,
        state: GameState,
        valid_moves: List[Position],
        rng: Optional[Random] = None,
    ) -> PolicyOutput:
        action = self.agent.select_action(state, valid_moves, rng)
        mask = build_action_mask(valid_moves)
        allowed_indices = [index for index, value in enumerate(mask) if value == 1]
        probability = 1.0 / len(allowed_indices) if allowed_indices else 1.0
        action_probabilities = {}
        for index in allowed_indices:
            if index == 64:
                action_probabilities["PASS"] = probability
            else:
                row, col = index // 8, index % 8
                action_probabilities[f"{row},{col}"] = probability
        return PolicyOutput(
            distribution_type="full_action_space",
            action_probabilities=action_probabilities,
            selected_action=action,
            state_value=None,
        )
