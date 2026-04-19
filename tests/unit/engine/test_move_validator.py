from engine.board import Board
from engine.move_validator import (
    get_flippable_directions,
    get_flippable_positions,
    get_valid_moves,
    is_valid_move,
)
from engine.types import CellState, Player


def test_get_valid_moves_returns_initial_black_moves():
    board = Board.create_initial()

    assert get_valid_moves(board, Player.BLACK) == [
        (2, 3),
        (3, 2),
        (4, 5),
        (5, 4),
    ]


def test_get_valid_moves_returns_initial_white_moves():
    board = Board.create_initial()

    assert get_valid_moves(board, Player.WHITE) == [
        (2, 4),
        (3, 5),
        (4, 2),
        (5, 3),
    ]


def test_is_valid_move_rejects_occupied_and_out_of_bounds_cells():
    board = Board.create_initial()

    assert is_valid_move(board, Player.BLACK, (3, 3)) is False
    assert is_valid_move(board, Player.BLACK, (-1, 0)) is False
    assert is_valid_move(board, Player.BLACK, (8, 8)) is False


def test_is_valid_move_rejects_empty_cell_that_flips_nothing():
    board = Board.create_initial()

    assert is_valid_move(board, Player.BLACK, (0, 0)) is False


def test_get_flippable_positions_returns_expected_cells():
    board = Board.create_initial()

    assert get_flippable_positions(board, Player.BLACK, (2, 3)) == [(3, 3)]


def test_get_flippable_directions_returns_expected_direction():
    board = Board.create_initial()

    assert get_flippable_directions(board, Player.BLACK, (2, 3)) == [(1, 0)]


def test_multi_direction_flip_case_returns_all_positions_and_directions():
    board = Board.from_matrix([[CellState.EMPTY.value for _ in range(8)] for _ in range(8)])
    board.set_cell((4, 1), CellState.BLACK)
    board.set_cell((1, 4), CellState.BLACK)
    board.set_cell((1, 1), CellState.BLACK)
    board.set_cell((4, 2), CellState.WHITE)
    board.set_cell((4, 3), CellState.WHITE)
    board.set_cell((2, 4), CellState.WHITE)
    board.set_cell((3, 4), CellState.WHITE)
    board.set_cell((2, 2), CellState.WHITE)
    board.set_cell((3, 3), CellState.WHITE)

    flipped = sorted(get_flippable_positions(board, Player.BLACK, (4, 4)))
    directions = sorted(get_flippable_directions(board, Player.BLACK, (4, 4)))

    assert flipped == [(2, 2), (2, 4), (3, 3), (3, 4), (4, 2), (4, 3)]
    assert directions == [(-1, -1), (-1, 0), (0, -1)]
