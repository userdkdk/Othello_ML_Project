import pytest
from types import SimpleNamespace

torch = pytest.importorskip("torch")
from torch.optim import Adam

from engine.types import Player
from training.cnn_policy_agent import load_cnn_checkpoint, save_cnn_checkpoint
from training.cnn_model import CNNPolicyValueModel
from training.episode import Episode, TurnRecord
from training.heuristic_agent import HeuristicAgent
from training.random_agent import RandomAgent
from training.self_play_runner import run_self_play
from training.training_pipeline import PolicyTrainingPipeline
from training.trainer import PolicyValueTrainer


def test_policy_value_trainer_trains_on_completed_episode_turns(tmp_path):
    result = run_self_play(
        black_agent=RandomAgent(),
        white_agent=HeuristicAgent(),
        num_games=2,
        seed=53,
    )
    model = CNNPolicyValueModel()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    trainer = PolicyValueTrainer(model, optimizer)

    report = trainer.train(
        result.episodes,
        epochs=2,
        checkpoint_path=str(tmp_path / "trainer-loop.pt"),
        checkpoint_version="cnn-trainer-loop-v1",
    )

    assert report.epochs == 2
    assert report.steps == 2
    assert report.samples == sum(len(episode.turns) for episode in result.episodes)
    assert report.policy_loss >= 0.0
    assert report.value_loss >= 0.0
    assert report.checkpoint_path is not None
    assert report.to_dict()["samples"] == report.samples


def test_policy_value_trainer_excludes_failed_episodes():
    class InvalidPassAgent:
        name = "invalid-pass-agent"
        version = "invalid-pass-v1"

        def select_action(self, state, valid_moves, rng=None):
            return "PASS"

    result = run_self_play(
        black_agent=InvalidPassAgent(),
        white_agent=HeuristicAgent(),
        num_games=1,
        seed=59,
    )
    model = CNNPolicyValueModel()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    trainer = PolicyValueTrainer(model, optimizer)

    with pytest.raises(ValueError):
        trainer.train(result.episodes)


def test_policy_value_trainer_ignores_failed_episode_when_completed_episode_exists():
    completed_result = run_self_play(
        black_agent=RandomAgent(),
        white_agent=HeuristicAgent(),
        num_games=1,
        seed=71,
    )
    failed_result = run_self_play(
        black_agent=RandomAgent(),
        white_agent=HeuristicAgent(),
        num_games=1,
        seed=73,
    )
    failed_episode = failed_result.episodes[0]
    failed_episode.mark_failed("TEST_FAILURE", "forced failure for exclusion check")

    model = CNNPolicyValueModel()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    trainer = PolicyValueTrainer(model, optimizer)

    report = trainer.train([completed_result.episodes[0], failed_episode])

    assert report.samples == len(completed_result.episodes[0].turns)
    assert report.steps == 1


def test_policy_value_trainer_can_reencode_when_encoded_state_missing():
    result = run_self_play(
        black_agent=RandomAgent(),
        white_agent=HeuristicAgent(),
        num_games=1,
        seed=61,
    )
    for turn in result.episodes[0].turns:
        turn.encoded_state = None

    model = CNNPolicyValueModel()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    trainer = PolicyValueTrainer(model, optimizer)

    report = trainer.train(result.episodes)

    assert report.samples == len(result.episodes[0].turns)
    assert report.steps == 1


def test_policy_value_trainer_accepts_pass_action_targets():
    encoded_state = [
        [[0.0 for _ in range(8)] for _ in range(8)]
        for _ in range(4)
    ]
    episode = Episode(
        episode_id="pass-episode",
        seed=79,
        policy_black_version="test-black-v1",
        policy_white_version="test-white-v1",
        turns=[
            TurnRecord(
                turn_index=0,
                player=Player.BLACK,
                state={
                    "board": [["EMPTY" for _ in range(8)] for _ in range(8)],
                    "current_player": "BLACK",
                    "status": {"is_finished": False, "winner": None},
                    "move_history": [],
                    "last_move": None,
                },
                action="PASS",
                valid_moves=[],
                action_mask=[0] * 64 + [1],
                encoded_state=encoded_state,
                reward=0.0,
            )
        ],
    )

    model = CNNPolicyValueModel()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    trainer = PolicyValueTrainer(model, optimizer)

    report = trainer.train([episode])

    assert report.samples == 1
    assert report.steps == 1


def test_policy_value_trainer_can_resume_from_checkpoint_and_accumulate_training_state(tmp_path):
    initial_result = run_self_play(
        black_agent=RandomAgent(),
        white_agent=HeuristicAgent(),
        num_games=1,
        seed=83,
    )
    resumed_result = run_self_play(
        black_agent=HeuristicAgent(),
        white_agent=RandomAgent(),
        num_games=1,
        seed=89,
    )
    checkpoint_path = tmp_path / "resume-trainer-loop.pt"

    first_model = CNNPolicyValueModel()
    first_optimizer = Adam(first_model.parameters(), lr=0.01)
    first_trainer = PolicyValueTrainer(first_model, first_optimizer)
    first_report = first_trainer.train(
        initial_result.episodes,
        epochs=2,
        checkpoint_path=str(checkpoint_path),
        checkpoint_version="cnn-resume-v1",
    )

    resumed_model = CNNPolicyValueModel()
    resumed_optimizer = Adam(resumed_model.parameters(), lr=0.01)
    resumed_trainer = PolicyValueTrainer(
        resumed_model,
        resumed_optimizer,
        resume_from_checkpoint=str(checkpoint_path),
    )
    resumed_report = resumed_trainer.train(
        resumed_result.episodes,
        epochs=3,
        checkpoint_path=str(checkpoint_path),
        checkpoint_version="cnn-resume-v1",
    )

    assert first_report.total_epochs == 2
    assert first_report.total_steps == 2
    assert resumed_report.resumed_from_checkpoint == str(checkpoint_path)
    assert resumed_report.total_epochs == 5
    assert resumed_report.total_steps == 5
    assert resumed_optimizer.state_dict()["state"]


def test_policy_value_trainer_resume_requires_training_state_and_optimizer(tmp_path):
    checkpoint_path = tmp_path / "resume-missing-state.pt"
    model = CNNPolicyValueModel()
    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "model_version": "cnn-resume-v2",
        },
        checkpoint_path,
    )

    resumed_model = CNNPolicyValueModel()
    resumed_optimizer = Adam(resumed_model.parameters(), lr=0.01)

    with pytest.raises(ValueError):
        PolicyValueTrainer(
            resumed_model,
            resumed_optimizer,
            resume_from_checkpoint=str(checkpoint_path),
        )


def test_policy_value_trainer_determine_promoted_tracks_uses_three_track_rules():
    model = CNNPolicyValueModel()
    optimizer = Adam(model.parameters(), lr=0.01)
    trainer = PolicyValueTrainer(model, optimizer)
    heuristic_report = SimpleNamespace(
        failures=0,
        black_side_win_rate=0.71,
        white_side_win_rate=0.72,
        balanced_eval_score=0.705,
    )
    current_best_reports = {
        "best_black": SimpleNamespace(failures=0, black_side_win_rate=0.56),
        "best_white": SimpleNamespace(failures=0, white_side_win_rate=0.57),
        "best_balanced": SimpleNamespace(failures=0, balanced_eval_score=0.58),
    }

    promoted = trainer.determine_promoted_tracks(
        heuristic_report=heuristic_report,
        current_best_reports=current_best_reports,
    )

    assert promoted == ["best_black", "best_white", "best_balanced"]


def test_policy_value_trainer_run_iteration_reports_promoted_tracks(tmp_path):
    result = run_self_play(
        black_agent=RandomAgent(),
        white_agent=HeuristicAgent(),
        num_games=1,
        seed=97,
    )
    model = CNNPolicyValueModel()
    optimizer = Adam(model.parameters(), lr=0.01)
    trainer = PolicyValueTrainer(model, optimizer)

    heuristic_report = SimpleNamespace(
        failures=0,
        black_side_win_rate=0.71,
        white_side_win_rate=0.72,
        balanced_eval_score=0.73,
    )
    current_best_reports = {
        "best_black": SimpleNamespace(failures=0, black_side_win_rate=0.56),
        "best_white": SimpleNamespace(failures=0, white_side_win_rate=0.57),
        "best_balanced": SimpleNamespace(failures=0, balanced_eval_score=0.58),
    }

    call_count = {"value": 0}

    def fake_evaluate_candidate(*args, **kwargs):
        call_count["value"] += 1
        if call_count["value"] == 1:
            return heuristic_report
        track_order = ["best_black", "best_white", "best_balanced"]
        return current_best_reports[track_order[call_count["value"] - 2]]

    trainer.evaluate_candidate = fake_evaluate_candidate

    report = trainer.run_iteration(
        result.episodes,
        epochs=1,
        latest_checkpoint_path=str(tmp_path / "latest-training.pt"),
        checkpoint_version="cnn-iter-v1",
        heuristic_agent=HeuristicAgent(),
        heuristic_games_per_side=1,
        current_best_agents={
            "best_black": RandomAgent(version="best-black-v1"),
            "best_white": RandomAgent(version="best-white-v1"),
            "best_balanced": RandomAgent(version="best-balanced-v1"),
        },
        current_best_games_per_side=1,
    )

    assert report.latest_checkpoint_path == str(tmp_path / "latest-training.pt")
    assert report.promoted_tracks == ["best_black", "best_white", "best_balanced"]
    assert report.total_iterations == 1


def test_policy_training_pipeline_runs_self_play_and_saves_training_and_inference_track_checkpoints(tmp_path):
    model = CNNPolicyValueModel()
    optimizer = Adam(model.parameters(), lr=0.01)
    trainer = PolicyValueTrainer(model, optimizer)
    pipeline = PolicyTrainingPipeline(trainer)

    heuristic_report = SimpleNamespace(
        failures=0,
        black_side_win_rate=0.71,
        white_side_win_rate=0.72,
        balanced_eval_score=0.73,
    )
    current_best_reports = {
        "best_black": SimpleNamespace(failures=0, black_side_win_rate=0.56),
        "best_white": SimpleNamespace(failures=0, white_side_win_rate=0.57),
        "best_balanced": SimpleNamespace(failures=0, balanced_eval_score=0.58),
    }

    call_count = {"value": 0}

    def fake_evaluate_candidate(*args, **kwargs):
        call_count["value"] += 1
        if call_count["value"] == 1:
            return heuristic_report
        track_order = ["best_black", "best_white", "best_balanced"]
        return current_best_reports[track_order[call_count["value"] - 2]]

    trainer.evaluate_candidate = fake_evaluate_candidate

    current_best_checkpoint_paths = {}
    for track in ("best_black", "best_white", "best_balanced"):
        checkpoint_path = tmp_path / f"{track}-current.pt"
        save_cnn_checkpoint(
            checkpoint_path,
            CNNPolicyValueModel(),
            version=f"{track}-v1",
        )
        current_best_checkpoint_paths[track] = str(checkpoint_path)

    best_training_checkpoint_paths = {
        track: str(tmp_path / f"{track}-training.pt")
        for track in ("best_black", "best_white", "best_balanced")
    }
    best_inference_checkpoint_paths = {
        track: str(tmp_path / f"{track}-inference.pt")
        for track in ("best_black", "best_white", "best_balanced")
    }

    result = pipeline.run_iteration(
        num_self_play_games=1,
        self_play_seed=101,
        episodes_output_path=str(tmp_path / "episodes.jsonl"),
        epochs=1,
        latest_checkpoint_path=str(tmp_path / "latest-training.pt"),
        checkpoint_version="cnn-pipeline-v1",
        heuristic_agent=HeuristicAgent(),
        heuristic_games_per_side=1,
        current_best_checkpoint_paths=current_best_checkpoint_paths,
        current_best_games_per_side=1,
        best_training_checkpoint_paths=best_training_checkpoint_paths,
        best_inference_checkpoint_paths=best_inference_checkpoint_paths,
    )

    assert result.written_episode_count == 1
    assert result.training_report.latest_checkpoint_path == str(tmp_path / "latest-training.pt")
    assert result.training_report.promoted_tracks == ["best_black", "best_white", "best_balanced"]
    assert sorted(result.current_best_agents.keys()) == ["best_balanced", "best_black", "best_white"]
    assert result.current_best_agents["best_black"].version == "best_black-v1"

    saved_training = load_cnn_checkpoint(best_training_checkpoint_paths["best_black"])
    assert saved_training.track == "best_black"
    assert saved_training.optimizer_state_dict is not None
    assert saved_training.training_state["completed_iterations"] == 1
    assert saved_training.evaluation_metadata["black_side_win_rate"] == pytest.approx(0.71)
    assert saved_training.evaluation_metadata["balanced_eval_score"] == pytest.approx(0.73)

    saved_inference = load_cnn_checkpoint(best_inference_checkpoint_paths["best_balanced"])
    assert saved_inference.track == "best_balanced"
    assert saved_inference.optimizer_state_dict is None
    assert saved_inference.training_state == {}
    assert saved_inference.evaluation_metadata["white_side_win_rate"] == pytest.approx(0.72)
