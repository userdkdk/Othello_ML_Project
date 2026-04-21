from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Any, Dict, List, Optional, Sequence, Union

from engine.types import GameState, Position
from training.action_mask import PASS_INDEX, action_to_index, build_action_mask, index_to_action
from training.agents import Agent, RandomAgent
from training.state_encoder import encode_state

try:
    import torch
except ModuleNotFoundError:  # pragma: no cover - exercised in non-torch local envs
    torch = None


@dataclass
class PolicyOutput:
    distribution_type: str
    action_probabilities: dict[str, float]
    selected_action: Union[Position, str]
    state_value: Optional[float] = None


class PolicyClient:
    def __init__(
        self,
        agent: Optional[Agent] = None,
        model: Optional[Any] = None,
        model_version: str = "cnn-v1",
        device: str = "cpu",
    ) -> None:
        self.agent = agent or RandomAgent()
        self.model = model
        self.model_version = model_version
        self.device = device
        if self.model is not None and hasattr(self.model, "to"):
            self.model = self.model.to(self.device)

    def predict(
        self,
        state: GameState,
        valid_moves: List[Position],
        rng: Optional[Random] = None,
    ) -> PolicyOutput:
        if self.model is not None:
            return self._predict_with_model(state, valid_moves)
        return self._predict_with_agent(state, valid_moves, rng)

    def _predict_with_agent(
        self,
        state: GameState,
        valid_moves: List[Position],
        rng: Optional[Random] = None,
    ) -> PolicyOutput:
        action = self.agent.select_action(state, valid_moves, rng)
        action_probabilities = _mask_to_uniform_probabilities(build_action_mask(valid_moves))
        return PolicyOutput(
            distribution_type="full_action_space",
            action_probabilities=action_probabilities,
            selected_action=action,
            state_value=None,
        )

    def _predict_with_model(
        self,
        state: GameState,
        valid_moves: List[Position],
    ) -> PolicyOutput:
        mask = build_action_mask(valid_moves)
        logits, state_value = self._run_model(encode_state(state))
        probabilities = _masked_softmax(logits, mask)
        selected_index = max(
            (index for index, value in enumerate(probabilities) if value > 0.0),
            key=lambda index: probabilities[index],
            default=PASS_INDEX,
        )
        action = index_to_action(selected_index)
        action_probabilities = _probabilities_to_dict(probabilities)
        return PolicyOutput(
            distribution_type="full_action_space",
            action_probabilities=action_probabilities,
            selected_action=action,
            state_value=state_value,
        )

    def _run_model(
        self,
        encoded_state: Sequence[Sequence[Sequence[float]]],
    ) -> tuple[List[float], float]:
        if torch is None:
            raise RuntimeError("torch is required to use model-based policy prediction")

        from training.cnn_model import encoded_state_to_tensor

        self.model.eval()
        with torch.no_grad():
            inputs = encoded_state_to_tensor(encoded_state).unsqueeze(0).to(self.device)
            policy_logits, value = self.model(inputs)
        return policy_logits.squeeze(0).detach().cpu().tolist(), float(value.reshape(-1)[0].item())


def policy_output_to_dict(policy_output: PolicyOutput) -> Dict[str, Any]:
    selected_action = (
        {"kind": "PASS", "position": None}
        if policy_output.selected_action == "PASS"
        else {"kind": "MOVE", "position": list(policy_output.selected_action)}
    )
    return {
        "distribution_type": policy_output.distribution_type,
        "action_probabilities": policy_output.action_probabilities,
        "selected_action": selected_action,
        "state_value": policy_output.state_value,
    }


def _mask_to_uniform_probabilities(mask: Sequence[int]) -> dict[str, float]:
    allowed_indices = [index for index, value in enumerate(mask) if value == 1]
    probability = 1.0 / len(allowed_indices) if allowed_indices else 1.0
    probabilities = [0.0] * len(mask)
    for index in allowed_indices:
        probabilities[index] = probability
    return _probabilities_to_dict(probabilities)


def _masked_softmax(logits: Sequence[float], mask: Sequence[int]) -> List[float]:
    if torch is None:
        raise RuntimeError("torch is required to apply masked softmax")

    logits_tensor = torch.tensor(logits, dtype=torch.float32)
    mask_tensor = torch.tensor(mask, dtype=torch.bool)
    masked_logits = logits_tensor.masked_fill(~mask_tensor, float("-inf"))
    if not mask_tensor.any():
        masked_logits[PASS_INDEX] = 0.0
    probabilities = torch.softmax(masked_logits, dim=0)
    return probabilities.detach().cpu().tolist()


def _probabilities_to_dict(probabilities: Sequence[float]) -> dict[str, float]:
    action_probabilities: dict[str, float] = {}
    for index, probability in enumerate(probabilities):
        if probability <= 0.0:
            continue
        if index == PASS_INDEX:
            action_probabilities["PASS"] = probability
            continue
        row, col = index_to_action(index)
        action_probabilities[f"{row},{col}"] = probability
    return action_probabilities
