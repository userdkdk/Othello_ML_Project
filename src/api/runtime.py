from __future__ import annotations

import json
from importlib.util import find_spec
from pathlib import Path
from typing import Any, Dict, Optional

from engine.game_engine import (
    apply_move,
    create_new_game,
    get_valid_moves_for_current_player,
    pass_turn,
)
from engine.types import CellState, GameState
from fastapi.responses import JSONResponse
from training.agents import HeuristicAgent, RandomAgent
from training.cnn_policy_agent import load_cnn_policy_agent

from api import app_state
from api.app_state import RuntimeSession
from api.schemas import NewGameRequest


ROOT_DIR = Path(__file__).resolve().parents[2]
BASE_DIR = Path(__file__).resolve().parent
DEFAULT_INFERENCE_CHECKPOINT_CANDIDATES = [
    ROOT_DIR / "checkpoints" / "best-balanced-inference.pt",
    ROOT_DIR / "checkpoints" / "best_balanced_inference.pt",
    BASE_DIR / "checkpoints" / "best-balanced-inference.pt",
    BASE_DIR / "checkpoints" / "best_balanced_inference.pt",
]
KNOWN_CHECKPOINT_SLOTS = [
    ("best_balanced_inference", ROOT_DIR / "checkpoints" / "best-balanced-inference.pt"),
    ("best_black_inference", ROOT_DIR / "checkpoints" / "best-black-inference.pt"),
    ("best_white_inference", ROOT_DIR / "checkpoints" / "best-white-inference.pt"),
    ("best_balanced_training", ROOT_DIR / "checkpoints" / "best-balanced-training.pt"),
    ("best_black_training", ROOT_DIR / "checkpoints" / "best-black-training.pt"),
    ("best_white_training", ROOT_DIR / "checkpoints" / "best-white-training.pt"),
    ("latest_training", ROOT_DIR / "checkpoints" / "latest-training.pt"),
]
DEFAULT_TRAINING_STATE_PATH = ROOT_DIR / "runs" / "latest" / "training_state.json"


def normalize_runtime_token(value: str) -> str:
    return value.strip().lower().replace("-", "_")


def resolve_mode(mode: str) -> str:
    normalized = normalize_runtime_token(mode)
    valid_modes = {"human_vs_human", "human_vs_model", "model_vs_model"}
    if normalized not in valid_modes:
        raise ValueError(f"INVALID_MODE:{mode}")
    return normalized


def resolve_checkpoint_reference(checkpoint_reference: str) -> Path:
    reference = checkpoint_reference.strip()
    explicit_path = Path(reference)
    if explicit_path.exists():
        return explicit_path

    normalized = normalize_runtime_token(reference)
    for slot_name, slot_path in KNOWN_CHECKPOINT_SLOTS:
        aliases = {
            slot_name,
            slot_name.replace("_", "-"),
            slot_name.removesuffix("_inference"),
            slot_name.removesuffix("_training"),
            slot_name.removesuffix("_inference").replace("_", "-"),
            slot_name.removesuffix("_training").replace("_", "-"),
            Path(slot_path).stem,
        }
        if normalized in {normalize_runtime_token(alias) for alias in aliases}:
            return slot_path

    return explicit_path


def json_error(
    error_code: str,
    message: str,
    *,
    status_code: int = 400,
    extra: Optional[dict[str, Any]] = None,
) -> JSONResponse:
    payload = {
        "error_code": error_code,
        "message": message,
    }
    if extra:
        payload.update(extra)
    return JSONResponse(status_code=status_code, content=payload)


def runtime_supports_model_loading() -> bool:
    return find_spec("torch") is not None


def resolve_default_checkpoint_path() -> Optional[Path]:
    for candidate in DEFAULT_INFERENCE_CHECKPOINT_CANDIDATES:
        if candidate.exists():
            return candidate
    return None


def _load_policy_agent_from_checkpoint(checkpoint_path: Path) -> Any:
    try:
        return load_cnn_policy_agent(checkpoint_path)
    except ModuleNotFoundError as error:
        missing = error.name or "torch"
        raise ValueError(f"MODEL_RUNTIME_UNAVAILABLE:{missing}") from error
    except Exception as error:  # pragma: no cover - depends on checkpoint payload
        raise ValueError(f"CHECKPOINT_LOAD_FAILED:{checkpoint_path}:{error}") from error


def default_agent_for_path(
    checkpoint_path: Optional[str],
    *,
    fallback_name: str,
    runtime_warnings: list[str],
) -> tuple[Any, str, Optional[str]]:
    if checkpoint_path is not None:
        explicit_path = resolve_checkpoint_reference(checkpoint_path)
        if not explicit_path.exists():
            raise ValueError(f"CHECKPOINT_NOT_FOUND:{checkpoint_path}")
        agent = _load_policy_agent_from_checkpoint(explicit_path)
        return agent, f"checkpoint:{explicit_path.name}", str(explicit_path)

    resolved_path = resolve_default_checkpoint_path()
    if resolved_path is not None:
        try:
            agent = _load_policy_agent_from_checkpoint(resolved_path)
            return agent, f"checkpoint:{resolved_path.name}", str(resolved_path)
        except ValueError as error:
            runtime_warnings.append(str(error))

    if fallback_name == "heuristic":
        agent = HeuristicAgent()
        return agent, f"{agent.name}:{agent.version}", None

    agent = RandomAgent()
    return agent, f"{agent.name}:{agent.version}", None


def normalize_human_side(mode: str, human_side: Optional[str]) -> Optional[str]:
    if mode != "human_vs_model":
        return None
    if human_side is not None:
        normalized = human_side.strip().upper().replace("-", "_")
        if normalized in {"BLACK", "WHITE"}:
            return normalized
    return "BLACK"


def build_session(payload: NewGameRequest) -> RuntimeSession:
    state = create_new_game()
    mode = resolve_mode(payload.mode)

    human_side = normalize_human_side(mode, payload.human_side)
    runtime_warnings: list[str] = []

    if mode == "human_vs_human":
        return RuntimeSession(
            state=state,
            mode=mode,
            black_agent_label="human",
            white_agent_label="human",
        )

    if mode == "human_vs_model":
        model_agent, model_label, resolved_checkpoint = default_agent_for_path(
            payload.black_checkpoint_path if human_side == "WHITE" else payload.white_checkpoint_path,
            fallback_name="heuristic",
            runtime_warnings=runtime_warnings,
        )
        if human_side == "BLACK":
            return RuntimeSession(
                state=state,
                mode=mode,
                human_side=human_side,
                white_agent=model_agent,
                black_agent_label="human",
                white_agent_label=model_label,
                white_checkpoint_path=resolved_checkpoint,
                runtime_warnings=runtime_warnings,
            )
        return RuntimeSession(
            state=state,
            mode=mode,
            human_side=human_side,
            black_agent=model_agent,
            black_agent_label=model_label,
            white_agent_label="human",
            black_checkpoint_path=resolved_checkpoint,
            runtime_warnings=runtime_warnings,
        )

    black_agent, black_label, black_checkpoint_path = default_agent_for_path(
        payload.black_checkpoint_path,
        fallback_name="heuristic",
        runtime_warnings=runtime_warnings,
    )
    white_agent, white_label, white_checkpoint_path = default_agent_for_path(
        payload.white_checkpoint_path,
        fallback_name="heuristic",
        runtime_warnings=runtime_warnings,
    )
    return RuntimeSession(
        state=state,
        mode="model_vs_model",
        black_agent=black_agent,
        white_agent=white_agent,
        black_agent_label=black_label,
        white_agent_label=white_label,
        black_checkpoint_path=black_checkpoint_path,
        white_checkpoint_path=white_checkpoint_path,
        runtime_warnings=runtime_warnings,
    )


def player_is_human(session: RuntimeSession, player: str) -> bool:
    if session.mode == "human_vs_human":
        return True
    if session.mode == "human_vs_model":
        return session.human_side == player
    return False


def current_turn_actor(session: RuntimeSession) -> str:
    return "human" if player_is_human(session, session.state.current_player.value) else "model"


def select_agent_for_current_player(session: RuntimeSession) -> Optional[Any]:
    return session.black_agent if session.state.current_player.value == "BLACK" else session.white_agent


def serialize_state(state: GameState) -> Dict[str, Any]:
    counts = state.board.count_cells()
    return {
        "board": state.board.to_strings(),
        "current_player": state.current_player.value,
        "counts": {
            "BLACK": counts[CellState.BLACK],
            "WHITE": counts[CellState.WHITE],
            "EMPTY": counts[CellState.EMPTY],
        },
        "status": {
            "is_finished": state.status.is_finished,
            "winner": state.status.winner.value if state.status.winner else None,
        },
        "valid_moves": [{"row": row, "col": col} for row, col in get_valid_moves_for_current_player(state)],
        "move_history": [
            {"row": move[0], "col": move[1]} if isinstance(move, tuple) else move
            for move in state.move_history
        ],
        "last_move": (
            {"row": state.last_move[0], "col": state.last_move[1]}
            if isinstance(state.last_move, tuple)
            else state.last_move
        ),
        "mode": app_state.SESSION.mode,
        "human_side": app_state.SESSION.human_side,
        "current_turn_actor": current_turn_actor(app_state.SESSION),
        "model_runtime_available": runtime_supports_model_loading(),
        "runtime_warnings": list(app_state.SESSION.runtime_warnings),
        "agents": {
            "BLACK": {
                "kind": "human" if app_state.SESSION.black_agent is None else "model",
                "label": app_state.SESSION.black_agent_label,
                "checkpoint_path": app_state.SESSION.black_checkpoint_path,
            },
            "WHITE": {
                "kind": "human" if app_state.SESSION.white_agent is None else "model",
                "label": app_state.SESSION.white_agent_label,
                "checkpoint_path": app_state.SESSION.white_checkpoint_path,
            },
        },
    }


def serialize_result(result: Any) -> Dict[str, Any]:
    return {
        "success": result.success,
        "applied_move": (
            {"row": result.applied_move[0], "col": result.applied_move[1]}
            if result.applied_move is not None
            else None
        ),
        "applied_player": result.applied_player.value if result.applied_player else None,
        "flipped_positions": [{"row": row, "col": col} for row, col in result.flipped_positions],
        "next_player": result.next_player.value if result.next_player else None,
        "status": {
            "is_finished": result.status.is_finished,
            "winner": result.status.winner.value if result.status.winner else None,
        },
        "error_code": result.error_code.value if result.error_code else None,
    }


def custom_error_result(error_code: str) -> Dict[str, Any]:
    return {
        "success": False,
        "applied_move": None,
        "applied_player": None,
        "flipped_positions": [],
        "next_player": None,
        "status": {
            "is_finished": app_state.SESSION.state.status.is_finished,
            "winner": app_state.SESSION.state.status.winner.value if app_state.SESSION.state.status.winner else None,
        },
        "error_code": error_code,
    }


def checkpoint_kind(slot_name: str) -> str:
    return "training" if "training" in slot_name or slot_name == "latest_training" else "inference"


def checkpoint_metadata(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "exists": False,
            "load_status": "missing",
            "metadata": {},
        }
    try:
        import torch
    except ModuleNotFoundError:
        return {
            "exists": True,
            "load_status": "dependency_missing",
            "error_code": "TORCH_NOT_INSTALLED",
            "metadata": {},
        }

    try:
        payload = torch.load(path, map_location="cpu")
    except Exception as error:  # pragma: no cover
        return {
            "exists": True,
            "load_status": "load_failed",
            "error_code": "CHECKPOINT_LOAD_FAILED",
            "message": str(error),
            "metadata": {},
        }

    metadata: dict[str, Any] = {}
    if isinstance(payload, dict):
        for key in (
            "model_version",
            "track",
            "saved_at",
            "black_side_win_rate",
            "white_side_win_rate",
            "balanced_eval_score",
        ):
            if key in payload:
                metadata[key] = payload[key]
        training_state = payload.get("training_state")
        if isinstance(training_state, dict):
            for key in ("completed_iterations", "completed_epochs", "completed_steps"):
                if key in training_state:
                    metadata[key] = training_state[key]

    return {
        "exists": True,
        "load_status": "ok",
        "metadata": metadata,
    }


def checkpoint_inventory() -> dict[str, Any]:
    seen: set[Path] = set()
    items: list[dict[str, Any]] = []

    for slot_name, path in KNOWN_CHECKPOINT_SLOTS:
        seen.add(path)
        item = {
            "slot": slot_name,
            "kind": checkpoint_kind(slot_name),
            "path": str(path),
            **checkpoint_metadata(path),
        }
        items.append(item)

    for path in sorted((ROOT_DIR / "checkpoints").glob("*.pt")):
        if path in seen:
            continue
        item = {
            "slot": path.stem,
            "kind": "training" if "training" in path.stem else "inference",
            "path": str(path),
            **checkpoint_metadata(path),
        }
        items.append(item)

    return {"items": items}


def load_training_state_snapshot() -> Optional[dict[str, Any]]:
    if not DEFAULT_TRAINING_STATE_PATH.exists():
        return None
    try:
        return json.loads(DEFAULT_TRAINING_STATE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def training_state_snapshot() -> dict[str, Any]:
    persisted_state = load_training_state_snapshot()
    if persisted_state is not None:
        return {
            "session": persisted_state.get("session", {}),
            "epoch_tracking": persisted_state.get("epoch_tracking"),
            "latest_iteration": persisted_state.get("latest_iteration"),
            "history": persisted_state.get("history", []),
            "checkpoint_inventory": checkpoint_inventory(),
            "last_comparison": app_state.LAST_TRAINING_COMPARISON,
        }
    return {
        "session": {
            "status": "idle",
            "active_stage": None,
            "message": "training ops API is not implemented yet",
        },
        "epoch_tracking": None,
        "latest_iteration": None,
        "history": [],
        "checkpoint_inventory": checkpoint_inventory(),
        "last_comparison": app_state.LAST_TRAINING_COMPARISON,
    }


def step_current_model_turn() -> Dict[str, Any]:
    if app_state.SESSION.state.status.is_finished:
        return {
            "state": serialize_state(app_state.SESSION.state),
            "result": custom_error_result("GAME_ALREADY_FINISHED"),
        }

    if player_is_human(app_state.SESSION, app_state.SESSION.state.current_player.value):
        return {
            "state": serialize_state(app_state.SESSION.state),
            "result": custom_error_result("NOT_MODEL_TURN"),
        }

    agent = select_agent_for_current_player(app_state.SESSION)
    valid_moves = get_valid_moves_for_current_player(app_state.SESSION.state)
    action = agent.select_action(app_state.SESSION.state.clone(), valid_moves)
    result = (
        pass_turn(app_state.SESSION.state)
        if action == "PASS"
        else apply_move(app_state.SESSION.state, action)
    )
    return {"state": serialize_state(app_state.SESSION.state), "result": serialize_result(result)}
