from __future__ import annotations

from engine.board import Board
from engine.types import CellState, Player, Position, opponent_of


DIRECTIONS = (
    (-1, -1),
    (-1, 0),
    (-1, 1),
    (0, -1),
    (0, 1),
    (1, -1),
    (1, 0),
    (1, 1),
)


def _player_cell(player: Player) -> CellState:
    return CellState.BLACK if player == Player.BLACK else CellState.WHITE


def _opponent_cell(player: Player) -> CellState:
    return _player_cell(opponent_of(player))


def get_flippable_positions(
    board: Board,
    player: Player,
    position: Position,
) -> list[Position]:
    if not board.is_in_bounds(position):
        return []
    if board.get_cell(position) != CellState.EMPTY:
        return []

    own_cell = _player_cell(player)
    opponent_cell = _opponent_cell(player)
    flippable: list[Position] = []

    for row_delta, col_delta in DIRECTIONS:
        path: list[Position] = []
        row, col = position[0] + row_delta, position[1] + col_delta

        while board.is_in_bounds((row, col)):
            current = board.get_cell((row, col))
            if current == opponent_cell:
                path.append((row, col))
                row += row_delta
                col += col_delta
                continue
            if current == own_cell and path:
                flippable.extend(path)
            break

    return flippable


def get_flippable_directions(
    board: Board,
    player: Player,
    position: Position,
) -> list[tuple[int, int]]:
    if not board.is_in_bounds(position):
        return []
    if board.get_cell(position) != CellState.EMPTY:
        return []

    own_cell = _player_cell(player)
    opponent_cell = _opponent_cell(player)
    directions: list[tuple[int, int]] = []

    for row_delta, col_delta in DIRECTIONS:
        saw_opponent = False
        row, col = position[0] + row_delta, position[1] + col_delta

        while board.is_in_bounds((row, col)):
            current = board.get_cell((row, col))
            if current == opponent_cell:
                saw_opponent = True
                row += row_delta
                col += col_delta
                continue
            if current == own_cell and saw_opponent:
                directions.append((row_delta, col_delta))
            break

    return directions


def is_valid_move(
    board: Board,
    player: Player,
    position: Position,
) -> bool:
    return bool(get_flippable_positions(board, player, position))


def get_valid_moves(
    board: Board,
    player: Player,
) -> list[Position]:
    valid_moves: list[Position] = []
    for row in range(8):
        for col in range(8):
            position = (row, col)
            if is_valid_move(board, player, position):
                valid_moves.append(position)
    return valid_moves
