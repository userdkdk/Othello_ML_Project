from __future__ import annotations

from typing import List, Sequence, Union

from engine.types import Position


PASS_INDEX = 64
ACTION_SPACE_SIZE = 65


def action_to_index(action: Union[Position, str]) -> int:
    if action == "PASS":
        return PASS_INDEX
    row, col = action
    return row * 8 + col


def index_to_action(index: int) -> Union[Position, str]:
    if index == PASS_INDEX:
        return "PASS"
    return index // 8, index % 8


def build_action_mask(valid_moves: Sequence[Position]) -> List[int]:
    mask = [0] * ACTION_SPACE_SIZE
    if not valid_moves:
        mask[PASS_INDEX] = 1
        return mask

    for move in valid_moves:
        mask[action_to_index(move)] = 1
    return mask
