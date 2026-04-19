from __future__ import annotations

from engine.board import Board
from engine.move_validator import get_flippable_positions, get_valid_moves
from engine.types import (
    CellState,
    GameResult,
    GameState,
    GameStatus,
    MoveErrorCode,
    MoveResult,
    Player,
    Position,
    opponent_of,
)


def _player_cell(player: Player) -> CellState:
    return CellState.BLACK if player == Player.BLACK else CellState.WHITE


def _winner_from_board(board: Board) -> GameResult:
    counts = board.count_cells()
    if counts[CellState.BLACK] > counts[CellState.WHITE]:
        return GameResult.BLACK_WIN
    if counts[CellState.WHITE] > counts[CellState.BLACK]:
        return GameResult.WHITE_WIN
    return GameResult.DRAW


def _failure_result(
    state: GameState,
    error_code: MoveErrorCode,
) -> MoveResult:
    return MoveResult(
        success=False,
        applied_move=None,
        applied_player=None,
        flipped_positions=[],
        next_player=None,
        status=GameStatus(
            is_finished=state.status.is_finished,
            winner=state.status.winner,
        ),
        error_code=error_code,
    )


def create_new_game() -> GameState:
    return GameState(
        board=Board.create_initial(),
        current_player=Player.BLACK,
        status=GameStatus(is_finished=False, winner=None),
    )


def get_valid_moves_for_current_player(state: GameState) -> list[Position]:
    return get_valid_moves(state.board, state.current_player)


def evaluate_game_status(
    board: Board,
    current_player: Player,
) -> GameStatus:
    counts = board.count_cells()
    if counts[CellState.EMPTY] == 0:
        return GameStatus(is_finished=True, winner=_winner_from_board(board))

    current_moves = get_valid_moves(board, current_player)
    opponent_moves = get_valid_moves(board, opponent_of(current_player))
    if not current_moves and not opponent_moves:
        return GameStatus(is_finished=True, winner=_winner_from_board(board))

    return GameStatus(is_finished=False, winner=None)


def apply_move(
    state: GameState,
    position: Position,
) -> MoveResult:
    if state.status.is_finished:
        return _failure_result(state, MoveErrorCode.GAME_ALREADY_FINISHED)

    if not state.board.is_in_bounds(position):
        return _failure_result(state, MoveErrorCode.OUT_OF_BOUNDS)

    if state.board.get_cell(position) != CellState.EMPTY:
        return _failure_result(state, MoveErrorCode.CELL_NOT_EMPTY)

    flipped_positions = get_flippable_positions(state.board, state.current_player, position)
    if not flipped_positions:
        return _failure_result(state, MoveErrorCode.NO_FLIPS)

    state.board.set_cell(position, _player_cell(state.current_player))
    for flipped_position in flipped_positions:
        state.board.set_cell(flipped_position, _player_cell(state.current_player))

    applied_player = state.current_player
    next_player = opponent_of(state.current_player)
    state.current_player = next_player
    state.status = evaluate_game_status(state.board, state.current_player)
    state.last_move = position
    state.move_history.append(position)

    return MoveResult(
        success=True,
        applied_move=position,
        applied_player=applied_player,
        flipped_positions=flipped_positions,
        next_player=state.current_player,
        status=state.status,
        error_code=None,
    )


def pass_turn(
    state: GameState,
) -> MoveResult:
    if state.status.is_finished:
        return _failure_result(state, MoveErrorCode.GAME_ALREADY_FINISHED)

    if get_valid_moves(state.board, state.current_player):
        return _failure_result(state, MoveErrorCode.PASS_NOT_ALLOWED)

    applied_player = state.current_player
    state.current_player = opponent_of(state.current_player)
    state.status = evaluate_game_status(state.board, state.current_player)
    state.last_move = "PASS"
    state.move_history.append("PASS")

    return MoveResult(
        success=True,
        applied_move=None,
        applied_player=applied_player,
        flipped_positions=[],
        next_player=state.current_player,
        status=state.status,
        error_code=None,
    )
