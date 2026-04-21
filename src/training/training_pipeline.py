from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional

from training.agents import CNNPolicyAgent
from training.cnn_policy_agent import load_cnn_policy_agent
from training.episode_storage import write_episodes_jsonl
from training.self_play_runner import SelfPlayResult, run_self_play
from training.trainer import ModelTrainingReport, PolicyValueTrainer


@dataclass
class PolicyTrainingIterationResult:
    self_play_result: SelfPlayResult
    training_report: ModelTrainingReport
    written_episode_count: int = 0
    current_best_agents: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "self_play_result": self.self_play_result.to_dict(),
            "training_report": self.training_report.to_dict(),
            "written_episode_count": self.written_episode_count,
            "current_best_tracks": sorted(self.current_best_agents.keys()),
        }


class PolicyTrainingPipeline:
    def __init__(self, trainer: PolicyValueTrainer) -> None:
        self.trainer = trainer

    def run_iteration(
        self,
        *,
        num_self_play_games: int,
        self_play_seed: int = 0,
        self_play_black_agent: Optional[Any] = None,
        self_play_white_agent: Optional[Any] = None,
        episodes_output_path: Optional[str] = None,
        episodes_output_mode: str = "w",
        epochs: int = 1,
        latest_checkpoint_path: Optional[str] = None,
        checkpoint_version: Optional[str] = None,
        checkpoint_model_kwargs: Optional[dict[str, Any]] = None,
        heuristic_agent: Optional[Any] = None,
        heuristic_games_per_side: int = 0,
        heuristic_seed: int = 0,
        current_best_checkpoint_paths: Optional[dict[str, str]] = None,
        current_best_games_per_side: int = 0,
        current_best_seed: int = 1000,
        best_training_checkpoint_paths: Optional[dict[str, str]] = None,
        best_inference_checkpoint_paths: Optional[dict[str, str]] = None,
        self_play_progress_callback: Optional[Callable[[int, int], None]] = None,
        train_progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> PolicyTrainingIterationResult:
        candidate_version = checkpoint_version or getattr(self.trainer.model, "model_version", "cnn-v1")
        black_agent = self_play_black_agent or CNNPolicyAgent(
            model=self.trainer.model,
            version=candidate_version,
            device=self.trainer.device,
        )
        white_agent = self_play_white_agent or CNNPolicyAgent(
            model=self.trainer.model,
            version=candidate_version,
            device=self.trainer.device,
        )

        self_play_result = run_self_play(
            black_agent=black_agent,
            white_agent=white_agent,
            num_games=num_self_play_games,
            seed=self_play_seed,
            progress_callback=self_play_progress_callback,
        )

        written_episode_count = 0
        if episodes_output_path is not None:
            written_episode_count = write_episodes_jsonl(
                episodes_output_path,
                self_play_result.episodes,
                mode=episodes_output_mode,
            )

        current_best_agents = _load_current_best_agents(current_best_checkpoint_paths)
        training_report = self.trainer.run_iteration(
            self_play_result.episodes,
            epochs=epochs,
            latest_checkpoint_path=latest_checkpoint_path,
            checkpoint_version=checkpoint_version,
            checkpoint_model_kwargs=checkpoint_model_kwargs,
            heuristic_agent=heuristic_agent,
            heuristic_games_per_side=heuristic_games_per_side,
            heuristic_seed=heuristic_seed,
            current_best_agents=current_best_agents,
            current_best_games_per_side=current_best_games_per_side,
            current_best_seed=current_best_seed,
            best_training_checkpoint_paths=best_training_checkpoint_paths,
            best_inference_checkpoint_paths=best_inference_checkpoint_paths,
            train_progress_callback=train_progress_callback,
        )
        return PolicyTrainingIterationResult(
            self_play_result=self_play_result,
            training_report=training_report,
            written_episode_count=written_episode_count,
            current_best_agents=current_best_agents,
        )


def _load_current_best_agents(
    current_best_checkpoint_paths: Optional[dict[str, str]],
) -> Dict[str, Any]:
    if not current_best_checkpoint_paths:
        return {}

    agents: Dict[str, Any] = {}
    for track, checkpoint_path in current_best_checkpoint_paths.items():
        agents[track] = load_cnn_policy_agent(checkpoint_path)
    return agents


__all__ = ["PolicyTrainingIterationResult", "PolicyTrainingPipeline"]
