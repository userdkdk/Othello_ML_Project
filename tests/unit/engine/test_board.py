from engine.board import Board
from engine.types import CellState


def test_create_initial_sets_standard_othello_layout():
    board = Board.create_initial()

    assert board.get_cell((3, 3)) == CellState.WHITE
    assert board.get_cell((3, 4)) == CellState.BLACK
    assert board.get_cell((4, 3)) == CellState.BLACK
    assert board.get_cell((4, 4)) == CellState.WHITE


def test_count_cells_matches_initial_counts():
    board = Board.create_initial()

    counts = board.count_cells()

    assert counts[CellState.BLACK] == 2
    assert counts[CellState.WHITE] == 2
    assert counts[CellState.EMPTY] == 60


def test_clone_returns_independent_copy():
    original = Board.create_initial()
    copied = original.clone()

    copied.set_cell((0, 0), CellState.BLACK)

    assert original.get_cell((0, 0)) == CellState.EMPTY
    assert copied.get_cell((0, 0)) == CellState.BLACK


def test_from_matrix_normalizes_string_values():
    board = Board.from_matrix(
        [[CellState.EMPTY.value for _ in range(8)] for _ in range(8)]
    )

    assert board.get_cell((0, 0)) == CellState.EMPTY
    assert board.to_strings()[0][0] == CellState.EMPTY.value


def test_is_in_bounds_and_access_reject_out_of_bounds_positions():
    board = Board.create_initial()

    assert board.is_in_bounds((-1, 0)) is False
    assert board.is_in_bounds((8, 8)) is False

    try:
        board.get_cell((-1, 0))
        assert False, "expected IndexError"
    except IndexError:
        pass

    try:
        board.set_cell((8, 8), CellState.BLACK)
        assert False, "expected IndexError"
    except IndexError:
        pass
