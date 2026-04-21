from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter

from api import app_state
from api.runtime import (
    build_session,
    custom_error_result,
    json_error,
    player_is_human,
    serialize_result,
    serialize_state,
    step_current_model_turn,
)
from api.schemas import MoveRequest, NewGameRequest
from engine.game_engine import apply_move, pass_turn


router = APIRouter()


@router.get("/api/state")
def get_state() -> Dict[str, Any]:
    return serialize_state(app_state.SESSION.state)


@router.post("/api/new")
def new_game(payload: Optional[NewGameRequest] = None) -> Any:
    try:
        app_state.SESSION = build_session(payload or NewGameRequest())
    except ValueError as error:
        error_text = str(error)
        error_code, _, remainder = error_text.partition(":")
        message = remainder or error_code
        return json_error(
            error_code,
            message,
            extra={"state": serialize_state(app_state.SESSION.state)},
        )
    return {"state": serialize_state(app_state.SESSION.state)}


@router.post("/api/move")
def move(payload: MoveRequest) -> Dict[str, Any]:
    if not player_is_human(app_state.SESSION, app_state.SESSION.state.current_player.value):
        return {"state": serialize_state(app_state.SESSION.state), "result": custom_error_result("NOT_HUMAN_TURN")}

    result = apply_move(app_state.SESSION.state, (payload.row, payload.col))
    return {"state": serialize_state(app_state.SESSION.state), "result": serialize_result(result)}


@router.post("/api/pass")
def do_pass() -> Dict[str, Any]:
    if not player_is_human(app_state.SESSION, app_state.SESSION.state.current_player.value):
        return {"state": serialize_state(app_state.SESSION.state), "result": custom_error_result("NOT_HUMAN_TURN")}

    result = pass_turn(app_state.SESSION.state)
    return {"state": serialize_state(app_state.SESSION.state), "result": serialize_result(result)}


@router.post("/api/step")
def step_model() -> Dict[str, Any]:
    return step_current_model_turn()
