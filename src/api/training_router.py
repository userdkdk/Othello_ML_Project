from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from api import app_state
from api.runtime import json_error, training_state_snapshot


router = APIRouter()


@router.get("/api/training/state")
def get_training_state() -> dict:
    return training_state_snapshot()


@router.get("/api/training/comparisons/latest")
def get_latest_training_comparison() -> dict:
    return {"comparison": app_state.LAST_TRAINING_COMPARISON}


def _training_ops_not_implemented(endpoint: str) -> JSONResponse:
    return json_error(
        "TRAINING_OPS_NOT_IMPLEMENTED",
        f"{endpoint} is not implemented yet in this runtime build",
        status_code=501,
    )


@router.post("/api/training/start")
def start_training() -> JSONResponse:
    return _training_ops_not_implemented("/api/training/start")


@router.post("/api/training/start-from-checkpoint")
def start_training_from_checkpoint() -> JSONResponse:
    return _training_ops_not_implemented("/api/training/start-from-checkpoint")


@router.post("/api/training/run-once")
def run_training_once() -> JSONResponse:
    return _training_ops_not_implemented("/api/training/run-once")


@router.post("/api/training/pause")
def pause_training() -> JSONResponse:
    return _training_ops_not_implemented("/api/training/pause")


@router.post("/api/training/resume-session")
def resume_training_session() -> JSONResponse:
    return _training_ops_not_implemented("/api/training/resume-session")


@router.post("/api/training/stop")
def stop_training() -> JSONResponse:
    return _training_ops_not_implemented("/api/training/stop")


@router.post("/api/training/compare")
def compare_checkpoints() -> JSONResponse:
    return _training_ops_not_implemented("/api/training/compare")
