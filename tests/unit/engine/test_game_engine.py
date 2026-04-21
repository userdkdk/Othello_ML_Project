from engine.game_engine import (
    apply_move,
    create_new_game,
    evaluate_game_status,
    get_valid_moves_for_current_player,
    pass_turn,
)
from engine.board import Board
from engine.types import CellState, GameResult, GameStatus, MoveErrorCode, Player


def test_create_new_game_returns_black_turn_and_initial_state():
    state = create_new_game()

    assert state.current_player == Player.BLACK
    assert state.status == GameStatus(is_finished=False, winner=None)
    assert get_valid_moves_for_current_player(state) == [
        (2, 3),
        (3, 2),
        (4, 5),
        (5, 4),
    ]


def test_apply_move_updates_board_turn_and_history():
    state = create_new_game()

    result = apply_move(state, (2, 3))

    assert result.success is True
    assert result.error_code is None
    assert result.flipped_positions == [(3, 3)]
    assert state.board.get_cell((2, 3)) == CellState.BLACK
    assert state.board.get_cell((3, 3)) == CellState.BLACK
    assert state.current_player == Player.WHITE
    assert state.last_move == (2, 3)
    assert state.move_history == [(2, 3)]


def test_apply_move_fails_without_mutating_state_for_invalid_position():
    state = create_new_game()
    before = state.clone()

    result = apply_move(state, (8, 8))

    assert result.success is False
    assert result.error_code == MoveErrorCode.OUT_OF_BOUNDS
    assert state.to_dict() == before.to_dict()


def test_apply_move_fails_for_occupied_cell_without_mutating_state():
    state = create_new_game()
    before = state.clone()

    result = apply_move(state, (3, 3))

    assert result.success is False
    assert result.error_code == MoveErrorCode.CELL_NOT_EMPTY
    assert state.to_dict() == before.to_dict()


def test_pass_turn_fails_when_valid_move_exists():
    state = create_new_game()
    before = state.clone()

    result = pass_turn(state)

    assert result.success is False
    assert result.error_code == MoveErrorCode.PASS_NOT_ALLOWED
    assert state.to_dict() == before.to_dict()


def test_pass_turn_succeeds_when_current_player_has_no_valid_move():
    board = Board.from_matrix([[CellState.BLACK.value for _ in range(8)] for _ in range(8)])
    board.set_cell((7, 7), CellState.EMPTY)
    board.set_cell((7, 6), CellState.WHITE)

    state = create_new_game()
    state.board = board
    state.current_player = Player.WHITE
    state.status = GameStatus(is_finished=False, winner=None)

    result = pass_turn(state)

    assert result.success is True
    assert result.error_code is None
    assert state.current_player == Player.BLACK
    assert state.last_move == "PASS"
    assert state.move_history == ["PASS"]


def test_apply_move_fails_after_game_finished():
    state = create_new_game()
    state.status = GameStatus(is_finished=True, winner=GameResult.BLACK)
    before = state.clone()

    result = apply_move(state, (2, 3))

    assert result.success is False
    assert result.error_code == MoveErrorCode.GAME_ALREADY_FINISHED
    assert state.to_dict() == before.to_dict()


def test_pass_turn_fails_after_game_finished():
    state = create_new_game()
    state.status = GameStatus(is_finished=True, winner=GameResult.DRAW)
    before = state.clone()

    result = pass_turn(state)

    assert result.success is False
    assert result.error_code == MoveErrorCode.GAME_ALREADY_FINISHED
    assert state.to_dict() == before.to_dict()


def test_evaluate_game_status_finishes_when_board_is_full():
    board = Board.from_matrix([[CellState.BLACK.value for _ in range(8)] for _ in range(8)])

    status = evaluate_game_status(board, Player.BLACK)

    assert status.is_finished is True
    assert status.winner == GameResult.BLACK


def test_evaluate_game_status_finishes_black_win_when_no_player_can_move():
    board = Board.from_matrix([[CellState.BLACK.value for _ in range(8)] for _ in range(8)])
    board.set_cell((7, 7), CellState.EMPTY)

    status = evaluate_game_status(board, Player.WHITE)

    assert status.is_finished is True
    assert status.winner == GameResult.BLACK


def test_evaluate_game_status_finishes_white_win_when_no_player_can_move():
    board = Board.from_matrix([[CellState.WHITE.value for _ in range(8)] for _ in range(8)])
    board.set_cell((7, 7), CellState.EMPTY)

    status = evaluate_game_status(board, Player.BLACK)

    assert status.is_finished is True
    assert status.winner == GameResult.WHITE


def test_evaluate_game_status_finishes_draw_when_no_player_can_move():
    board = Board.from_matrix([[CellState.BLACK.value for _ in range(8)] for _ in range(8)])
    for row in range(4):
        for col in range(8):
            board.set_cell((row, col), CellState.WHITE)

    status = evaluate_game_status(board, Player.WHITE)

    assert status.is_finished is True
    assert status.winner == GameResult.DRAW
