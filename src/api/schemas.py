from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class MoveRequest(BaseModel):
    row: int
    col: int


class NewGameRequest(BaseModel):
    mode: str = "human_vs_human"
    human_side: Optional[str] = None
    black_checkpoint_path: Optional[str] = None
    white_checkpoint_path: Optional[str] = None
