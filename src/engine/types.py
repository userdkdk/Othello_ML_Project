from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple, Union

if TYPE_CHECKING:
    from engine.board import Board


Position = Tuple[int, int]


class CellState(str, Enum):
    EMPTY = "EMPTY"
    BLACK = "BLACK"
    WHITE = "WHITE"


class Player(str, Enum):
    BLACK = "BLACK"
    WHITE = "WHITE"


class GameResult(str, Enum):
    BLACK = "BLACK"
    WHITE = "WHITE"
    DRAW = "DRAW"


class MoveErrorCode(str, Enum):
    OUT_OF_BOUNDS = "OUT_OF_BOUNDS"
    CELL_NOT_EMPTY = "CELL_NOT_EMPTY"
    NO_FLIPS = "NO_FLIPS"
    GAME_ALREADY_FINISHED = "GAME_ALREADY_FINISHED"
    PASS_NOT_ALLOWED = "PASS_NOT_ALLOWED"


@dataclass
class GameStatus:
    is_finished: bool
    winner: Optional[GameResult]


@dataclass
class MoveResult:
    success: bool
    applied_move: Optional[Position]
    applied_player: Optional[Player]
    flipped_positions: List[Position]
    next_player: Optional[Player]
    status: GameStatus
    error_code: Optional[MoveErrorCode]


@dataclass
class GameState:
    board: Board
    current_player: Player
    status: GameStatus
    move_history: List[Union[Position, str]] = field(default_factory=list)
    last_move: Optional[Union[Position, str]] = None

    def clone(self) -> "GameState":
        return GameState(
            board=self.board.clone(),
            current_player=self.current_player,
            status=GameStatus(
                is_finished=self.status.is_finished,
                winner=self.status.winner,
            ),
            move_history=list(self.move_history),
            last_move=self.last_move,
        )

    def to_dict(self) -> Dict[str, object]:
        return {
            "board": self.board.to_strings(),
            "current_player": self.current_player.value,
            "status": {
                "is_finished": self.status.is_finished,
                "winner": self.status.winner.value if self.status.winner else None,
            },
            "move_history": [
                list(move) if isinstance(move, tuple) else move
                for move in self.move_history
            ],
            "last_move": list(self.last_move) if isinstance(self.last_move, tuple) else self.last_move,
        }


def opponent_of(player: Player) -> Player:
    return Player.WHITE if player == Player.BLACK else Player.BLACK
