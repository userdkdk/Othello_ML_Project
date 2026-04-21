from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from engine.game_engine import create_new_game
from engine.types import GameState


@dataclass
class RuntimeSession:
    state: GameState
    mode: str = "human_vs_human"
    human_side: Optional[str] = None
    black_agent: Optional[Any] = None
    white_agent: Optional[Any] = None
    black_agent_label: str = "human"
    white_agent_label: str = "human"
    black_checkpoint_path: Optional[str] = None
    white_checkpoint_path: Optional[str] = None
    runtime_warnings: list[str] = field(default_factory=list)


SESSION = RuntimeSession(state=create_new_game())
LAST_TRAINING_COMPARISON: Optional[dict[str, Any]] = None
