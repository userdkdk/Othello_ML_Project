from __future__ import annotations

from typing import Iterable, Sequence, Tuple

import torch
from torch import Tensor, nn


MODEL_VERSION = "cnn-v1"
INPUT_CHANNELS = 4
BOARD_SIZE = 8
ACTION_SPACE_SIZE = 65


class CNNPolicyValueModel(nn.Module):
    def __init__(
        self,
        input_channels: int = INPUT_CHANNELS,
        channels: int = 64,
        num_blocks: int = 3,
    ) -> None:
        super().__init__()
        self.stem = nn.Sequential(
            nn.Conv2d(input_channels, channels, kernel_size=3, padding=1),
            nn.ReLU(),
        )
        self.trunk = nn.Sequential(
            *[ResidualBlock(channels) for _ in range(num_blocks)]
        )
        self.policy_head = nn.Sequential(
            nn.Conv2d(channels, 2, kernel_size=1),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(2 * BOARD_SIZE * BOARD_SIZE, ACTION_SPACE_SIZE),
        )
        self.value_head = nn.Sequential(
            nn.Conv2d(channels, 1, kernel_size=1),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(BOARD_SIZE * BOARD_SIZE, channels),
            nn.ReLU(),
            nn.Linear(channels, 1),
            nn.Tanh(),
        )

    def forward(self, x: Tensor) -> Tuple[Tensor, Tensor]:
        if x.ndim != 4:
            raise ValueError(f"expected 4D input (batch, channels, height, width), got {tuple(x.shape)}")
        features = self.trunk(self.stem(x))
        policy_logits = self.policy_head(features)
        value = self.value_head(features)
        return policy_logits, value


class ResidualBlock(nn.Module):
    def __init__(self, channels: int) -> None:
        super().__init__()
        self.layers = nn.Sequential(
            nn.Conv2d(channels, channels, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(channels, channels, kernel_size=3, padding=1),
        )
        self.activation = nn.ReLU()

    def forward(self, x: Tensor) -> Tensor:
        return self.activation(x + self.layers(x))


def encoded_state_to_tensor(encoded_state: Sequence[Sequence[Sequence[float]]]) -> Tensor:
    tensor = torch.tensor(encoded_state, dtype=torch.float32)
    if tensor.shape != (INPUT_CHANNELS, BOARD_SIZE, BOARD_SIZE):
        raise ValueError(
            f"expected encoded state shape {(INPUT_CHANNELS, BOARD_SIZE, BOARD_SIZE)}, got {tuple(tensor.shape)}"
        )
    return tensor


def encoded_states_to_batch(
    encoded_states: Iterable[Sequence[Sequence[Sequence[float]]]],
) -> Tensor:
    batch = torch.stack([encoded_state_to_tensor(state) for state in encoded_states], dim=0)
    return batch
