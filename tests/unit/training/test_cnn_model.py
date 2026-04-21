import pytest
from pathlib import Path

torch = pytest.importorskip("torch")
from torch import nn

from engine.game_engine import create_new_game, get_valid_moves_for_current_player
from training.agents import CNNPolicyAgent
from training.action_mask import PASS_INDEX, action_to_index
from training.cnn_policy_agent import load_cnn_checkpoint, load_cnn_policy_agent, save_cnn_checkpoint
from training.cnn_model import CNNPolicyValueModel, encoded_state_to_tensor
from training.policy_client import PolicyClient
from training.self_play_runner import run_self_play
from training.state_encoder import encode_state


def test_cnn_model_returns_policy_logits_and_value_shapes():
    state = create_new_game()
    encoded = encode_state(state)
    inputs = encoded_state_to_tensor(encoded).unsqueeze(0)

    model = CNNPolicyValueModel()
    policy_logits, value = model(inputs)

    assert tuple(policy_logits.shape) == (1, 65)
    assert tuple(value.shape) == (1, 1)


class DummyModel(nn.Module):
    def forward(self, x):  # noqa: D401 - simple test stub
        batch_size = x.shape[0]
        logits = torch.full((batch_size, 65), -10.0)
        logits[:, PASS_INDEX] = 100.0
        logits[:, action_to_index((2, 3))] = 50.0
        value = torch.tensor([[0.25]] * batch_size, dtype=torch.float32)
        return logits, value


def test_policy_client_masks_out_pass_when_valid_moves_exist():
    state = create_new_game()
    valid_moves = get_valid_moves_for_current_player(state)

    output = PolicyClient(model=DummyModel()).predict(state, valid_moves)

    assert output.selected_action == (2, 3)
    assert "PASS" not in output.action_probabilities
    assert output.state_value == pytest.approx(0.25)


def test_policy_client_selects_pass_when_no_valid_moves_exist():
    state = create_new_game()

    output = PolicyClient(model=DummyModel()).predict(state, [])

    assert output.selected_action == "PASS"
    assert output.action_probabilities["PASS"] == pytest.approx(1.0)


def test_cnn_policy_agent_can_select_action_from_policy_client():
    state = create_new_game()
    valid_moves = get_valid_moves_for_current_player(state)

    agent = CNNPolicyAgent(model=DummyModel())
    action = agent.select_action(state, valid_moves)

    assert action == (2, 3)


def test_load_cnn_policy_agent_from_checkpoint(tmp_path: Path):
    model = CNNPolicyValueModel()
    checkpoint_path = tmp_path / "cnn-agent.pt"
    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "model_version": "cnn-test-v2",
        },
        checkpoint_path,
    )

    agent = load_cnn_policy_agent(str(checkpoint_path))

    assert isinstance(agent, CNNPolicyAgent)
    assert agent.version == "cnn-test-v2"


def test_load_cnn_policy_agent_prefers_explicit_version_and_model_kwargs(tmp_path: Path):
    model = CNNPolicyValueModel(channels=32, num_blocks=2)
    checkpoint_path = tmp_path / "cnn-agent-kwargs.pt"
    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "model_version": "cnn-checkpoint-v1",
            "model_kwargs": {"channels": 32, "num_blocks": 2},
        },
        checkpoint_path,
    )

    agent = load_cnn_policy_agent(
        str(checkpoint_path),
        version="cnn-explicit-v9",
        model_kwargs={"channels": 32, "num_blocks": 2},
    )

    assert isinstance(agent, CNNPolicyAgent)
    assert agent.version == "cnn-explicit-v9"


def test_load_cnn_policy_agent_accepts_plain_state_dict_checkpoint(tmp_path: Path):
    model = CNNPolicyValueModel()
    checkpoint_path = tmp_path / "cnn-agent-state-dict.pt"
    torch.save(model.state_dict(), checkpoint_path)

    agent = load_cnn_policy_agent(str(checkpoint_path))

    assert isinstance(agent, CNNPolicyAgent)
    assert agent.version == "cnn-v1"


def test_load_cnn_policy_agent_prefers_model_state_dict_over_state_dict(tmp_path: Path):
    preferred_model = CNNPolicyValueModel(channels=32, num_blocks=2)
    fallback_model = CNNPolicyValueModel(channels=16, num_blocks=1)
    checkpoint_path = tmp_path / "cnn-agent-priority.pt"
    torch.save(
        {
            "model_state_dict": preferred_model.state_dict(),
            "state_dict": fallback_model.state_dict(),
            "model_kwargs": {"channels": 32, "num_blocks": 2},
        },
        checkpoint_path,
    )

    agent = load_cnn_policy_agent(
        str(checkpoint_path),
        model_kwargs={"channels": 32, "num_blocks": 2},
    )

    stem_weight = agent.model.state_dict()["stem.0.weight"]
    assert torch.equal(stem_weight, preferred_model.state_dict()["stem.0.weight"])


def test_load_cnn_policy_agent_rejects_metadata_only_dict_checkpoint(tmp_path: Path):
    checkpoint_path = tmp_path / "cnn-agent-invalid.pt"
    torch.save({"model_version": "cnn-bad-v1"}, checkpoint_path)

    with pytest.raises(ValueError):
        load_cnn_policy_agent(str(checkpoint_path))


def test_save_cnn_checkpoint_writes_recommended_payload(tmp_path: Path):
    model = CNNPolicyValueModel()
    checkpoint_path = tmp_path / "cnn-saved.pt"

    save_cnn_checkpoint(
        checkpoint_path,
        model,
        version="cnn-save-v3",
        model_kwargs={"channels": 64, "num_blocks": 3},
        extra_metadata={"saved_at": "2026-04-20T00:00:00Z"},
    )

    payload = torch.load(checkpoint_path)

    assert "model_state_dict" in payload
    assert payload["model_version"] == "cnn-save-v3"
    assert payload["model_kwargs"] == {"channels": 64, "num_blocks": 3}
    assert payload["saved_at"] == "2026-04-20T00:00:00Z"


def test_load_cnn_checkpoint_exposes_optional_training_metadata(tmp_path: Path):
    model = CNNPolicyValueModel()
    checkpoint_path = tmp_path / "cnn-training-state.pt"
    save_cnn_checkpoint(
        checkpoint_path,
        model,
        version="cnn-save-v4",
        extra_metadata={
            "optimizer_state_dict": {"state": {}, "param_groups": [{"lr": 0.001}]},
            "training_state": {"completed_epochs": 3, "completed_steps": 12},
        },
    )

    loaded = load_cnn_checkpoint(str(checkpoint_path))

    assert loaded.version == "cnn-save-v4"
    assert loaded.optimizer_state_dict == {"state": {}, "param_groups": [{"lr": 0.001}]}
    assert loaded.training_state == {"completed_epochs": 3, "completed_steps": 12}


def test_load_cnn_checkpoint_exposes_top_level_evaluation_metadata(tmp_path: Path):
    model = CNNPolicyValueModel()
    checkpoint_path = tmp_path / "cnn-eval-metadata.pt"
    save_cnn_checkpoint(
        checkpoint_path,
        model,
        version="cnn-save-v5",
        extra_metadata={
            "black_side_win_rate": 0.72,
            "white_side_win_rate": 0.61,
            "balanced_eval_score": 0.665,
            "track": "best_balanced",
        },
    )

    loaded = load_cnn_checkpoint(str(checkpoint_path))

    assert loaded.evaluation_metadata == {
        "black_side_win_rate": 0.72,
        "white_side_win_rate": 0.61,
        "balanced_eval_score": 0.665,
    }
    assert loaded.track == "best_balanced"


def test_cnn_policy_agent_can_run_self_play_and_record_version():
    result = run_self_play(
        black_agent=CNNPolicyAgent(model=DummyModel(), version="cnn-black-v1"),
        white_agent=CNNPolicyAgent(model=DummyModel(), version="cnn-white-v1"),
        num_games=1,
        seed=5,
    )

    assert len(result.episodes) == 1
    assert result.episodes[0].policy_black_version == "cnn-black-v1"
    assert result.episodes[0].policy_white_version == "cnn-white-v1"
    assert result.episodes[0].turns[0].policy_output is not None
