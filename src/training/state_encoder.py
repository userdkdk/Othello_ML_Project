from __future__ import annotations

from typing import Dict, List

from engine.types import CellState, GameState, Player


EncodedState = List[List[List[float]]]


def encode_state(state: GameState) -> EncodedState:
    current_is_black = 1.0 if state.current_player == Player.BLACK else 0.0
    board = state.board.to_strings()

    current_plane: List[List[float]] = []
    opponent_plane: List[List[float]] = []
    empty_plane: List[List[float]] = []
    player_plane: List[List[float]] = []

    current_color = CellState.BLACK.value if state.current_player == Player.BLACK else CellState.WHITE.value
    opponent_color = CellState.WHITE.value if state.current_player == Player.BLACK else CellState.BLACK.value

    for row in board:
        current_plane.append([1.0 if cell == current_color else 0.0 for cell in row])
        opponent_plane.append([1.0 if cell == opponent_color else 0.0 for cell in row])
        empty_plane.append([1.0 if cell == CellState.EMPTY.value else 0.0 for cell in row])
        player_plane.append([current_is_black for _ in row])

    return [current_plane, opponent_plane, empty_plane, player_plane]


def encoded_state_shape(encoded_state: EncodedState) -> Dict[str, int]:
    return {
        "planes": len(encoded_state),
        "height": len(encoded_state[0]) if encoded_state else 0,
        "width": len(encoded_state[0][0]) if encoded_state and encoded_state[0] else 0,
    }
