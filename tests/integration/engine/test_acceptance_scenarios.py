from engine.board import Board
from engine.game_engine import (
    apply_move,
    create_new_game,
    evaluate_game_status,
    get_valid_moves_for_current_player,
    pass_turn,
)
from engine.move_validator import get_valid_moves
from engine.types import CellState, GameResult, GameStatus, MoveErrorCode, Player


def test_initial_state_matches_acceptance_document():
    state = create_new_game()
    counts = state.board.count_cells()

    assert state.board.get_cell((3, 3)) == CellState.WHITE
    assert state.board.get_cell((3, 4)) == CellState.BLACK
    assert state.board.get_cell((4, 3)) == CellState.BLACK
    assert state.board.get_cell((4, 4)) == CellState.WHITE
    assert state.current_player == Player.BLACK
    assert counts[CellState.BLACK] == 2
    assert counts[CellState.WHITE] == 2
    assert counts[CellState.EMPTY] == 60


def test_initial_valid_moves_match_acceptance_document():
    state = create_new_game()

    assert get_valid_moves_for_current_player(state) == [
        (2, 3),
        (3, 2),
        (4, 5),
        (5, 4),
    ]
    assert get_valid_moves(state.board, Player.WHITE) == [
        (2, 4),
        (3, 5),
        (4, 2),
        (5, 3),
    ]


def test_black_move_at_2_3_flips_3_3_and_changes_turn():
    state = create_new_game()

    result = apply_move(state, (2, 3))

    assert result.success is True
    assert state.board.get_cell((2, 3)) == CellState.BLACK
    assert state.board.get_cell((3, 3)) == CellState.BLACK
    assert state.board.get_cell((3, 4)) == CellState.BLACK
    assert state.board.get_cell((4, 3)) == CellState.BLACK
    assert state.board.get_cell((4, 4)) == CellState.WHITE
    assert state.current_player == Player.WHITE


def test_multi_direction_flip_acceptance_scenario():
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

    state = create_new_game()
    state.board = board
    state.current_player = Player.BLACK
    state.status = GameStatus(is_finished=False, winner=None)

    result = apply_move(state, (4, 4))

    assert result.success is True
    assert state.board.get_cell((4, 4)) == CellState.BLACK
    assert state.board.get_cell((2, 2)) == CellState.BLACK
    assert state.board.get_cell((2, 4)) == CellState.BLACK
    assert state.board.get_cell((3, 3)) == CellState.BLACK
    assert state.board.get_cell((3, 4)) == CellState.BLACK
    assert state.board.get_cell((4, 2)) == CellState.BLACK
    assert state.board.get_cell((4, 3)) == CellState.BLACK


def test_invalid_moves_keep_state_unchanged():
    state = create_new_game()
    before = state.to_dict()

    occupied_result = apply_move(state, (3, 3))
    assert occupied_result.success is False
    assert occupied_result.error_code == MoveErrorCode.CELL_NOT_EMPTY
    assert state.to_dict() == before

    out_of_bounds_result = apply_move(state, (8, 8))
    assert out_of_bounds_result.success is False
    assert out_of_bounds_result.error_code == MoveErrorCode.OUT_OF_BOUNDS
    assert state.to_dict() == before

    no_flip_result = apply_move(state, (0, 0))
    assert no_flip_result.success is False
    assert no_flip_result.error_code == MoveErrorCode.NO_FLIPS
    assert state.to_dict() == before


def test_pass_and_consecutive_no_moves_finish_game():
    board = Board.from_matrix([[CellState.BLACK.value for _ in range(8)] for _ in range(8)])
    board.set_cell((7, 7), CellState.EMPTY)

    state = create_new_game()
    state.board = board
    state.current_player = Player.WHITE
    state.status = GameStatus(is_finished=False, winner=None)

    result = pass_turn(state)

    assert result.success is True
    assert state.current_player == Player.BLACK
    assert state.status.is_finished is True
    assert state.status.winner == GameResult.BLACK_WIN


def test_full_board_finishes_immediately_with_winner():
    board = Board.from_matrix([[CellState.WHITE.value for _ in range(8)] for _ in range(8)])

    status = evaluate_game_status(board, Player.BLACK)

    assert status.is_finished is True
    assert status.winner == GameResult.WHITE_WIN


def test_finished_game_rejects_move_and_pass():
    state = create_new_game()
    state.status = GameStatus(is_finished=True, winner=GameResult.DRAW)
    before = state.to_dict()

    move_result = apply_move(state, (2, 3))
    pass_result = pass_turn(state)

    assert move_result.success is False
    assert move_result.error_code == MoveErrorCode.GAME_ALREADY_FINISHED
    assert pass_result.success is False
    assert pass_result.error_code == MoveErrorCode.GAME_ALREADY_FINISHED
    assert state.to_dict() == before


def test_winner_evaluation_covers_black_white_and_draw():
    black_board = Board.from_matrix([[CellState.BLACK.value for _ in range(8)] for _ in range(8)])
    white_board = Board.from_matrix([[CellState.WHITE.value for _ in range(8)] for _ in range(8)])
    draw_board = Board.from_matrix([[CellState.BLACK.value for _ in range(8)] for _ in range(8)])
    for row in range(4):
        for col in range(8):
            draw_board.set_cell((row, col), CellState.WHITE)

    assert evaluate_game_status(black_board, Player.BLACK).winner == GameResult.BLACK_WIN
    assert evaluate_game_status(white_board, Player.BLACK).winner == GameResult.WHITE_WIN
    assert evaluate_game_status(draw_board, Player.BLACK).winner == GameResult.DRAW
