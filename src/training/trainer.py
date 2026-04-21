from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, List, Optional

from engine.board import Board
from engine.types import GameResult, GameState, GameStatus, Player
from training.action_mask import action_to_index
from training.episode import Episode
from training.state_encoder import encode_state

try:
    import torch
    from torch import nn
except ModuleNotFoundError:  # pragma: no cover - exercised in non-torch local envs
    torch = None
    nn = None


@dataclass
class TrainingReport:
    completed_episodes: int
    failed_episodes: int
    average_turns: float
    reward_distribution: Dict[str, int]

    def to_dict(self) -> Dict[str, object]:
        return {
            "completed_episodes": self.completed_episodes,
            "failed_episodes": self.failed_episodes,
            "average_turns": self.average_turns,
            "reward_distribution": self.reward_distribution,
        }


@dataclass
class ModelTrainingReport:
    iteration: int
    epochs: int
    steps: int
    samples: int
    policy_loss: float
    value_loss: float
    checkpoint_path: Optional[str] = None
    resumed_from_checkpoint: Optional[str] = None
    latest_checkpoint_path: Optional[str] = None
    promoted_tracks: List[str] = field(default_factory=list)
    best_training_checkpoint_paths: Dict[str, str] = field(default_factory=dict)
    best_inference_checkpoint_paths: Dict[str, str] = field(default_factory=dict)
    total_iterations: Optional[int] = None
    total_epochs: Optional[int] = None
    total_steps: Optional[int] = None

    def to_dict(self) -> Dict[str, object]:
        return {
            "iteration": self.iteration,
            "epochs": self.epochs,
            "steps": self.steps,
            "samples": self.samples,
            "policy_loss": self.policy_loss,
            "value_loss": self.value_loss,
            "checkpoint_path": self.checkpoint_path,
            "resumed_from_checkpoint": self.resumed_from_checkpoint,
            "latest_checkpoint_path": self.latest_checkpoint_path,
            "promoted_tracks": list(self.promoted_tracks),
            "best_training_checkpoint_paths": dict(self.best_training_checkpoint_paths),
            "best_inference_checkpoint_paths": dict(self.best_inference_checkpoint_paths),
            "total_iterations": self.total_iterations,
            "total_epochs": self.total_epochs,
            "total_steps": self.total_steps,
        }


class Trainer:
    def train(self, episodes: Iterable[Episode]) -> TrainingReport:
        episodes_list: List[Episode] = list(episodes)
        completed = [episode for episode in episodes_list if episode.status == "completed"]
        failed = [episode for episode in episodes_list if episode.status == "failed"]
        average_turns = (
            sum(len(episode.turns) for episode in completed) / len(completed)
            if completed
            else 0.0
        )
        reward_distribution = {
            "positive": sum(1 for episode in completed if (episode.final_reward or 0) > 0),
            "zero": sum(1 for episode in completed if (episode.final_reward or 0) == 0),
            "negative": sum(1 for episode in completed if (episode.final_reward or 0) < 0),
        }
        return TrainingReport(
            completed_episodes=len(completed),
            failed_episodes=len(failed),
            average_turns=average_turns,
            reward_distribution=reward_distribution,
        )


class PolicyValueTrainer:
    def __init__(
        self,
        model: Any,
        optimizer: Any,
        *,
        device: str = "cpu",
        resume_from_checkpoint: Optional[str] = None,
    ) -> None:
        if torch is None or nn is None:
            raise RuntimeError("torch is required to use PolicyValueTrainer")

        self.model = model.to(device)
        self.optimizer = optimizer
        self.device = device
        self.policy_loss_fn = nn.CrossEntropyLoss()
        self.value_loss_fn = nn.MSELoss()
        self.completed_iterations = 0
        self.completed_epochs = 0
        self.completed_steps = 0
        self.last_checkpoint_path: Optional[str] = None

        if resume_from_checkpoint is not None:
            self.load_checkpoint(resume_from_checkpoint)

    def load_checkpoint(
        self,
        checkpoint_path: str,
        *,
        version: Optional[str] = None,
        model_kwargs: Optional[dict[str, Any]] = None,
    ) -> None:
        from training.cnn_policy_agent import load_cnn_checkpoint

        loaded = load_cnn_checkpoint(
            checkpoint_path,
            device=self.device,
            version=version,
            model_kwargs=model_kwargs,
        )
        required_training_state_keys = {"completed_iterations", "completed_epochs", "completed_steps"}
        if loaded.optimizer_state_dict is None:
            raise ValueError("resume checkpoint does not contain optimizer_state_dict")
        if not required_training_state_keys.issubset(loaded.training_state):
            raise ValueError(
                "resume checkpoint does not contain required training_state keys: "
                "completed_iterations, completed_epochs, completed_steps"
            )

        self.model.load_state_dict(loaded.model.state_dict())
        self.model.to(self.device)
        self.optimizer.load_state_dict(loaded.optimizer_state_dict)
        self.completed_iterations = int(loaded.training_state["completed_iterations"])
        self.completed_epochs = int(loaded.training_state.get("completed_epochs", 0))
        self.completed_steps = int(loaded.training_state.get("completed_steps", 0))
        self.last_checkpoint_path = checkpoint_path

    def train(
        self,
        episodes: Iterable[Episode],
        *,
        epochs: int = 1,
        checkpoint_path: Optional[str] = None,
        checkpoint_version: Optional[str] = None,
        checkpoint_model_kwargs: Optional[dict[str, Any]] = None,
        checkpoint_extra_metadata: Optional[dict[str, Any]] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> ModelTrainingReport:
        resumed_from_checkpoint = self.last_checkpoint_path
        samples = _collect_training_samples(episodes)
        if not samples:
            raise ValueError("no completed episode samples available for training")

        from training.cnn_model import encoded_states_to_batch
        from training.cnn_policy_agent import save_cnn_checkpoint

        total_policy_loss = 0.0
        total_value_loss = 0.0
        steps = 0

        self.model.train()
        for epoch_index in range(epochs):
            inputs = encoded_states_to_batch(sample["encoded_state"] for sample in samples).to(self.device)
            policy_targets = torch.tensor(
                [sample["policy_target"] for sample in samples],
                dtype=torch.long,
                device=self.device,
            )
            value_targets = torch.tensor(
                [sample["value_target"] for sample in samples],
                dtype=torch.float32,
                device=self.device,
            ).unsqueeze(1)

            self.optimizer.zero_grad()
            policy_logits, values = self.model(inputs)
            policy_loss = self.policy_loss_fn(policy_logits, policy_targets)
            value_loss = self.value_loss_fn(values, value_targets)
            loss = policy_loss + value_loss
            loss.backward()
            self.optimizer.step()

            total_policy_loss += float(policy_loss.item())
            total_value_loss += float(value_loss.item())
            steps += 1
            if progress_callback is not None:
                progress_callback(epoch_index + 1, epochs)

        self.completed_iterations += 1
        self.completed_epochs += epochs
        self.completed_steps += steps
        saved_checkpoint_path = checkpoint_path
        if checkpoint_path is not None:
            extra_metadata = {
                "optimizer_state_dict": self.optimizer.state_dict(),
                "training_state": {
                    "completed_iterations": self.completed_iterations,
                    "completed_epochs": self.completed_epochs,
                    "completed_steps": self.completed_steps,
                    "last_run_epochs": epochs,
                    "last_run_steps": steps,
                    "last_run_samples": len(samples),
                },
            }
            if checkpoint_extra_metadata:
                extra_metadata.update(dict(checkpoint_extra_metadata))
            save_cnn_checkpoint(
                checkpoint_path,
                self.model,
                version=checkpoint_version or getattr(self.model, "model_version", "cnn-v1"),
                model_kwargs=checkpoint_model_kwargs,
                extra_metadata=extra_metadata,
            )
            self.last_checkpoint_path = checkpoint_path

        return ModelTrainingReport(
            iteration=self.completed_iterations,
            epochs=epochs,
            steps=steps,
            samples=len(samples),
            policy_loss=total_policy_loss / steps,
            value_loss=total_value_loss / steps,
            checkpoint_path=saved_checkpoint_path,
            resumed_from_checkpoint=resumed_from_checkpoint,
            latest_checkpoint_path=saved_checkpoint_path,
            total_iterations=self.completed_iterations,
            total_epochs=self.completed_epochs,
            total_steps=self.completed_steps,
        )

    def evaluate_candidate(
        self,
        opponent_agent: Any,
        *,
        num_games_per_side: int,
        seed: int = 0,
        version: Optional[str] = None,
    ) -> Any:
        from training.agents import CNNPolicyAgent
        from training.evaluator import Evaluator

        candidate_agent = CNNPolicyAgent(
            model=self.model,
            version=version or getattr(self.model, "model_version", "cnn-v1"),
            device=self.device,
        )
        return Evaluator().compare_agents(
            candidate_agent,
            opponent_agent,
            num_games_per_side=num_games_per_side,
            seed=seed,
        )

    def determine_promoted_tracks(
        self,
        *,
        heuristic_report: Any,
        current_best_reports: Optional[dict[str, Any]] = None,
    ) -> List[str]:
        if heuristic_report.failures != 0:
            return []

        metric_by_track = {
            "best_black": "black_side_win_rate",
            "best_white": "white_side_win_rate",
            "best_balanced": "balanced_eval_score",
        }
        heuristic_thresholds = {
            "best_black": 0.70,
            "best_white": 0.70,
            "best_balanced": 0.70,
        }
        current_best_thresholds = {
            "best_black": 0.55,
            "best_white": 0.55,
            "best_balanced": 0.55,
        }
        promoted: List[str] = []
        current_best_reports = current_best_reports or {}

        for track, metric_name in metric_by_track.items():
            heuristic_value = getattr(heuristic_report, metric_name)
            if heuristic_value is None or heuristic_value < heuristic_thresholds[track]:
                continue

            current_report = current_best_reports.get(track)
            if current_report is not None:
                if current_report.failures != 0:
                    continue
                current_value = getattr(current_report, metric_name)
                if current_value is None or current_value < current_best_thresholds[track]:
                    continue

            promoted.append(track)
        return promoted

    def run_iteration(
        self,
        episodes: Iterable[Episode],
        *,
        epochs: int = 1,
        latest_checkpoint_path: Optional[str] = None,
        checkpoint_version: Optional[str] = None,
        checkpoint_model_kwargs: Optional[dict[str, Any]] = None,
        heuristic_agent: Optional[Any] = None,
        heuristic_games_per_side: int = 0,
        heuristic_seed: int = 0,
        current_best_agents: Optional[dict[str, Any]] = None,
        current_best_games_per_side: int = 0,
        current_best_seed: int = 1000,
        best_training_checkpoint_paths: Optional[dict[str, str]] = None,
        best_inference_checkpoint_paths: Optional[dict[str, str]] = None,
        best_checkpoint_paths: Optional[dict[str, str]] = None,
        train_progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> ModelTrainingReport:
        report = self.train(
            episodes,
            epochs=epochs,
            checkpoint_path=latest_checkpoint_path,
            checkpoint_version=checkpoint_version,
            checkpoint_model_kwargs=checkpoint_model_kwargs,
            progress_callback=train_progress_callback,
        )
        if heuristic_agent is None or heuristic_games_per_side <= 0:
            return report

        heuristic_report = self.evaluate_candidate(
            heuristic_agent,
            num_games_per_side=heuristic_games_per_side,
            seed=heuristic_seed,
            version=checkpoint_version,
        )
        current_best_reports: dict[str, Any] = {}
        if current_best_agents and current_best_games_per_side > 0:
            track_offsets = {
                "best_black": 0,
                "best_white": 100,
                "best_balanced": 200,
            }
            for track, agent in current_best_agents.items():
                current_best_reports[track] = self.evaluate_candidate(
                    agent,
                    num_games_per_side=current_best_games_per_side,
                    seed=current_best_seed + track_offsets.get(track, 0),
                    version=checkpoint_version,
                )

        promoted_tracks = self.determine_promoted_tracks(
            heuristic_report=heuristic_report,
            current_best_reports=current_best_reports,
        )
        saved_best_training_paths: dict[str, str] = {}
        saved_best_inference_paths: dict[str, str] = {}
        if best_training_checkpoint_paths:
            for track in promoted_tracks:
                checkpoint_path = best_training_checkpoint_paths.get(track)
                if checkpoint_path is None:
                    continue
                self.save_track_checkpoint(
                    checkpoint_path,
                    track=track,
                    version=checkpoint_version or getattr(self.model, "model_version", "cnn-v1"),
                    model_kwargs=checkpoint_model_kwargs,
                    evaluation_report=heuristic_report if track == "best_balanced" else heuristic_report,
                    include_training_state=True,
                )
                saved_best_training_paths[track] = checkpoint_path
        if best_inference_checkpoint_paths or best_checkpoint_paths:
            inference_paths = best_inference_checkpoint_paths or best_checkpoint_paths
            for track in promoted_tracks:
                checkpoint_path = inference_paths.get(track)
                if checkpoint_path is None:
                    continue
                self.save_track_checkpoint(
                    checkpoint_path,
                    track=track,
                    version=checkpoint_version or getattr(self.model, "model_version", "cnn-v1"),
                    model_kwargs=checkpoint_model_kwargs,
                    evaluation_report=heuristic_report if track == "best_balanced" else heuristic_report,
                    include_training_state=False,
                )
                saved_best_inference_paths[track] = checkpoint_path

        report.promoted_tracks = promoted_tracks
        report.best_training_checkpoint_paths = saved_best_training_paths
        report.best_inference_checkpoint_paths = saved_best_inference_paths
        return report

    def save_track_checkpoint(
        self,
        checkpoint_path: str,
        *,
        track: str,
        version: str,
        model_kwargs: Optional[dict[str, Any]] = None,
        evaluation_report: Optional[Any] = None,
        include_training_state: bool = False,
    ) -> None:
        from training.cnn_policy_agent import save_cnn_checkpoint

        extra_metadata: dict[str, Any] = {"track": track}
        if evaluation_report is not None:
            for key in ("black_side_win_rate", "white_side_win_rate", "balanced_eval_score"):
                value = getattr(evaluation_report, key, None)
                if value is not None:
                    extra_metadata[key] = value
        if include_training_state:
            extra_metadata["optimizer_state_dict"] = self.optimizer.state_dict()
            extra_metadata["training_state"] = {
                "completed_iterations": self.completed_iterations,
                "completed_epochs": self.completed_epochs,
                "completed_steps": self.completed_steps,
            }
        save_cnn_checkpoint(
            checkpoint_path,
            self.model,
            version=version,
            model_kwargs=model_kwargs,
            extra_metadata=extra_metadata,
        )


def _collect_training_samples(episodes: Iterable[Episode]) -> List[Dict[str, Any]]:
    samples: List[Dict[str, Any]] = []
    for episode in episodes:
        if episode.status != "completed":
            continue
        for turn in episode.turns:
            if turn.reward is None:
                continue
            samples.append(
                {
                    "encoded_state": _resolve_encoded_state(turn),
                    "policy_target": action_to_index(turn.action),
                    "value_target": float(turn.reward),
                }
            )
    return samples


def _resolve_encoded_state(turn: Any) -> Any:
    if turn.encoded_state is not None:
        return turn.encoded_state
    return encode_state(_game_state_from_record(turn.state))


def _game_state_from_record(state_record: Dict[str, Any]) -> GameState:
    board = Board.from_matrix(state_record["board"])
    current_player = Player(state_record["current_player"])
    status_record = state_record["status"]
    status = GameStatus(
        is_finished=bool(status_record["is_finished"]),
        winner=None if status_record["winner"] is None else GameResult(status_record["winner"]),
    )
    move_history = [
        tuple(move) if isinstance(move, list) else move
        for move in state_record.get("move_history", [])
    ]
    last_move = state_record.get("last_move")
    if isinstance(last_move, list):
        last_move = tuple(last_move)
    return GameState(
        board=board,
        current_player=current_player,
        status=status,
        move_history=move_history,
        last_move=last_move,
    )
