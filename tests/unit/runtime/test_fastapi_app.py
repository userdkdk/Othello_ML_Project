from pathlib import Path

from fastapi import HTTPException
from fastapi.testclient import TestClient

import api.fastapi_app as fastapi_app
import api.runtime as runtime_api
from api.fastapi_app import app


client = TestClient(app)


def test_new_game_supports_human_vs_human_mode():
    response = client.post("/api/new", json={"mode": "human_vs_human"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["state"]["mode"] == "human_vs_human"
    assert payload["state"]["agents"]["BLACK"]["kind"] == "human"
    assert payload["state"]["agents"]["WHITE"]["kind"] == "human"


def test_new_game_supports_human_vs_model_mode_with_human_white():
    response = client.post("/api/new", json={"mode": "human_vs_model", "human_side": "WHITE"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["state"]["mode"] == "human_vs_model"
    assert payload["state"]["human_side"] == "WHITE"
    assert payload["state"]["agents"]["BLACK"]["kind"] == "model"
    assert payload["state"]["agents"]["WHITE"]["kind"] == "human"


def test_new_game_accepts_hyphenated_mode_and_human_side():
    response = client.post("/api/new", json={"mode": "human-vs-model", "human_side": "white"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["state"]["mode"] == "human_vs_model"
    assert payload["state"]["human_side"] == "WHITE"


def test_move_fails_when_it_is_not_human_turn():
    client.post("/api/new", json={"mode": "human_vs_model", "human_side": "WHITE"})

    response = client.post("/api/move", json={"row": 2, "col": 3})

    assert response.status_code == 200
    payload = response.json()
    assert payload["result"]["success"] is False
    assert payload["result"]["error_code"] == "NOT_HUMAN_TURN"


def test_step_advances_model_turn_in_human_vs_model():
    client.post("/api/new", json={"mode": "human_vs_model", "human_side": "WHITE"})

    response = client.post("/api/step")

    assert response.status_code == 200
    payload = response.json()
    assert payload["result"]["success"] is True
    assert payload["result"]["applied_player"] == "BLACK"
    assert payload["state"]["current_player"] == "WHITE"
    assert payload["state"]["current_turn_actor"] == "human"


def test_step_advances_model_vs_model_game():
    client.post("/api/new", json={"mode": "model_vs_model"})

    response = client.post("/api/step")

    assert response.status_code == 200
    payload = response.json()
    assert payload["result"]["success"] is True
    assert payload["result"]["applied_player"] == "BLACK"
    assert payload["state"]["mode"] == "model_vs_model"


def test_training_state_returns_idle_snapshot():
    response = client.get("/api/training/state")

    assert response.status_code == 200
    payload = response.json()
    assert payload["session"]["status"] == "idle"
    assert "checkpoint_inventory" in payload
    assert isinstance(payload["checkpoint_inventory"]["items"], list)


def test_training_state_reads_persisted_snapshot(monkeypatch, tmp_path: Path):
    state_path = tmp_path / "training_state.json"
    state_path.write_text(
        """
        {
          "session": {
            "status": "running",
            "active_stage": "train",
            "current_iteration": 3
          },
          "epoch_tracking": {
            "target_epochs": 10,
            "current_epoch": 6,
            "current_epoch_progress_percent": 60,
            "completed_epochs_after_run": 26
          },
          "latest_iteration": {
            "iteration": 2,
            "policy_loss": 0.12
          },
          "history": [
            {
              "iteration": 2
            }
          ]
        }
        """.strip(),
        encoding="utf-8",
    )
    monkeypatch.setattr(runtime_api, "DEFAULT_TRAINING_STATE_PATH", state_path)

    response = client.get("/api/training/state")

    assert response.status_code == 200
    payload = response.json()
    assert payload["session"]["status"] == "running"
    assert payload["session"]["active_stage"] == "train"
    assert payload["epoch_tracking"]["current_epoch_progress_percent"] == 60
    assert payload["epoch_tracking"]["current_epoch"] == 6
    assert payload["latest_iteration"]["iteration"] == 2
    assert payload["history"][0]["iteration"] == 2


def test_root_returns_controlled_error_when_frontend_build_is_missing(monkeypatch):
    def raise_missing():
        raise HTTPException(
            status_code=503,
            detail={
                "error_code": "FRONTEND_BUILD_MISSING",
                "message": "frontend build output was not found; run npm run build in frontend/",
            },
        )

    monkeypatch.setattr(fastapi_app, "serve_frontend_app", raise_missing)

    response = client.get("/")
    payload = response.json()
    assert response.status_code == 503
    assert payload["detail"]["error_code"] == "FRONTEND_BUILD_MISSING"


def test_explicit_checkpoint_failure_returns_controlled_error(monkeypatch, tmp_path: Path):
    checkpoint_path = tmp_path / "model.pt"
    checkpoint_path.write_bytes(b"not-a-real-checkpoint")

    def fail_loader(_path):
        raise ValueError("MODEL_RUNTIME_UNAVAILABLE:torch")

    monkeypatch.setattr(runtime_api, "_load_policy_agent_from_checkpoint", fail_loader)

    response = client.post(
        "/api/new",
        json={
            "mode": "model_vs_model",
            "black_checkpoint_path": str(checkpoint_path),
        },
    )

    assert response.status_code == 400
    payload = response.json()
    assert payload["error_code"] == "MODEL_RUNTIME_UNAVAILABLE"
    assert payload["message"] == "torch"


def test_checkpoint_slot_alias_with_hyphen_or_underscore_is_resolved(monkeypatch):
    def fail_loader(_path):
        raise ValueError("MODEL_RUNTIME_UNAVAILABLE:torch")

    monkeypatch.setattr(runtime_api, "_load_policy_agent_from_checkpoint", fail_loader)

    response = client.post(
        "/api/new",
        json={
            "mode": "model-vs-model",
            "black_checkpoint_path": "best-balanced-inference",
        },
    )

    assert response.status_code == 400
    payload = response.json()
    assert payload["error_code"] == "MODEL_RUNTIME_UNAVAILABLE"
    assert payload["message"] == "torch"
