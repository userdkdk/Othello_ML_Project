from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

from engine.types import GameResult, GameState, Player, Position


Action = Union[Position, str]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class TurnRecord:
    turn_index: int
    player: Player
    state: Dict[str, Any]
    action: Action
    valid_moves: List[Position]
    action_mask: List[int]
    encoded_state: Any
    policy_output: Optional[Dict[str, Any]] = None
    reward: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "turn_index": self.turn_index,
            "player": self.player.value,
            "state": self.state,
            "action": {
                "kind": "PASS" if self.action == "PASS" else "MOVE",
                "position": None if self.action == "PASS" else list(self.action),
            },
            "valid_moves": [list(move) for move in self.valid_moves],
            "action_mask": self.action_mask,
            "policy_output": self.policy_output,
            "reward": self.reward,
        }


@dataclass
class EpisodeFailure:
    error_code: str
    message: str
    failed_turn_index: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_code": self.error_code,
            "message": self.message,
            "failed_turn_index": self.failed_turn_index,
        }


@dataclass
class Episode:
    episode_id: str
    seed: int
    policy_black_version: str
    policy_white_version: str
    started_at: str = field(default_factory=utc_now_iso)
    finished_at: Optional[str] = None
    initial_state_type: str = "standard"
    initial_state: Optional[Dict[str, Any]] = None
    reward_perspective: str = "BLACK"
    final_reward: Optional[float] = None
    winner: Optional[str] = None
    status: str = "completed"
    turns: List[TurnRecord] = field(default_factory=list)
    failure: Optional[EpisodeFailure] = None

    def finalize(self, result: Optional[GameResult]) -> None:
        self.finished_at = utc_now_iso()
        if result is None:
            self.winner = None
            self.final_reward = None
            return

        if result == GameResult.BLACK:
            self.winner = "BLACK"
            self.final_reward = 1.0
        elif result == GameResult.WHITE:
            self.winner = "WHITE"
            self.final_reward = -1.0
        else:
            self.winner = "DRAW"
            self.final_reward = 0.0

        for turn in self.turns:
            turn.reward = self.final_reward

    def mark_failed(self, error_code: str, message: str, failed_turn_index: Optional[int] = None) -> None:
        self.status = "failed"
        self.finished_at = utc_now_iso()
        self.failure = EpisodeFailure(
            error_code=error_code,
            message=message,
            failed_turn_index=failed_turn_index,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "episode_id": self.episode_id,
            "status": self.status,
            "seed": self.seed,
            "policy_black_version": self.policy_black_version,
            "policy_white_version": self.policy_white_version,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "initial_state_type": self.initial_state_type,
            "initial_state": self.initial_state,
            "reward_perspective": self.reward_perspective,
            "final_reward": self.final_reward,
            "winner": self.winner,
            "turns": [turn.to_dict() for turn in self.turns],
            "failure": self.failure.to_dict() if self.failure else None,
        }
