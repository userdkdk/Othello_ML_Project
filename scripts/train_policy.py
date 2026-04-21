from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Callable

import torch

from training import (
    CNNPolicyValueModel,
    HeuristicAgent,
    PolicyTrainingPipeline,
    PolicyValueTrainer,
    RandomAgent,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a minimal self-play + policy/value training iteration.",
    )
    parser.add_argument("--output-dir", default="runs/latest", help="Directory for episodes, checkpoint, and summary.")
    parser.add_argument("--num-games", type=int, default=64, help="Number of self-play games to generate.")
    parser.add_argument("--self-play-seed", type=int, default=42, help="Base seed for self-play.")
    parser.add_argument("--epochs", type=int, default=5, help="Training epochs for the collected samples.")
    parser.add_argument("--learning-rate", type=float, default=1e-3, help="Optimizer learning rate.")
    parser.add_argument(
        "--black-agent",
        choices=("random", "heuristic"),
        default="random",
        help="Agent used as black during self-play data generation.",
    )
    parser.add_argument(
        "--white-agent",
        choices=("random", "heuristic"),
        default="heuristic",
        help="Agent used as white during self-play data generation.",
    )
    parser.add_argument(
        "--checkpoint-name",
        default="checkpoint.pt",
        help="Checkpoint filename written inside output-dir.",
    )
    parser.add_argument(
        "--episodes-name",
        default="episodes.jsonl",
        help="Episode jsonl filename written inside output-dir.",
    )
    parser.add_argument(
        "--summary-name",
        default="train_report.json",
        help="Summary json filename written inside output-dir.",
    )
    parser.add_argument(
        "--checkpoint-version",
        default="cnn-v1",
        help="Version string stored in the saved checkpoint.",
    )
    parser.add_argument(
        "--resume-from",
        default=None,
        help="Optional checkpoint path to resume optimizer/model/training state from.",
    )
    parser.add_argument(
        "--state-name",
        default="training_state.json",
        help="Training state snapshot filename written inside output-dir.",
    )
    return parser.parse_args()


def build_agent(agent_name: str):
    if agent_name == "random":
        return RandomAgent()
    if agent_name == "heuristic":
        return HeuristicAgent()
    raise ValueError(f"unsupported agent name: {agent_name}")


def build_progress_logger(label: str) -> Callable[[int, int], None]:
    last_percent = -1

    def log_progress(completed: int, total: int) -> None:
        nonlocal last_percent
        if total <= 0:
            return
        percent = int((completed / total) * 100)
        should_print = completed == total or completed == 1 or percent >= last_percent + 5
        if not should_print:
            return
        last_percent = percent
        print(f"[{label}] {percent:3d}% ({completed}/{total})", flush=True)

    return log_progress


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_state_snapshot(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_state_snapshot(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    state_path = output_dir / args.state_name

    model = CNNPolicyValueModel()
    optimizer = torch.optim.Adam(model.parameters(), lr=args.learning_rate)
    trainer = PolicyValueTrainer(
        model,
        optimizer,
        resume_from_checkpoint=args.resume_from,
    )
    pipeline = PolicyTrainingPipeline(trainer)
    next_iteration = trainer.completed_iterations + 1
    previous_state = read_state_snapshot(state_path)
    preserved_history = list(previous_state.get("history", []))
    session_id = previous_state.get("session", {}).get("session_id") or f"training-{utc_timestamp()}"
    created_at = previous_state.get("session", {}).get("created_at") or utc_timestamp()

    state_payload: dict[str, Any] = {
        "session": {
            "session_id": session_id,
            "status": "running",
            "current_iteration": next_iteration,
            "active_stage": "train",
            "created_at": created_at,
            "updated_at": utc_timestamp(),
            "start_from_checkpoint_path": args.resume_from,
            "latest_checkpoint_path": str(output_dir / args.checkpoint_name),
            "last_error": None,
        },
        "epoch_tracking": {
            "target_epochs": args.epochs,
            "current_epoch": 0,
            "current_epoch_progress_percent": 0,
            "completed_epochs_before_run": trainer.completed_epochs,
            "completed_epochs_after_run": trainer.completed_epochs,
        },
        "latest_iteration": None,
        "history": preserved_history,
    }

    def persist_state() -> None:
        state_payload["session"]["updated_at"] = utc_timestamp()
        write_state_snapshot(state_path, state_payload)

    def update_epoch_progress(completed: int, total: int) -> None:
        percent = 0 if total <= 0 else int((completed / total) * 100)
        state_payload["session"]["status"] = "running"
        state_payload["session"]["active_stage"] = "train"
        state_payload["session"]["current_iteration"] = next_iteration
        state_payload["epoch_tracking"]["target_epochs"] = total
        state_payload["epoch_tracking"]["current_epoch"] = completed
        state_payload["epoch_tracking"]["current_epoch_progress_percent"] = percent
        state_payload["epoch_tracking"]["completed_epochs_after_run"] = trainer.completed_epochs + completed
        persist_state()

    train_progress = build_progress_logger("train")

    def train_progress_callback(completed: int, total: int) -> None:
        train_progress(completed, total)
        update_epoch_progress(completed, total)

    persist_state()

    print(
        json.dumps(
            {
                "event": "training_started",
                "output_dir": str(output_dir),
                "num_games": args.num_games,
                "epochs": args.epochs,
                "resume_from": args.resume_from,
            },
            ensure_ascii=False,
        ),
        flush=True,
    )

    try:
        iteration_result = pipeline.run_iteration(
            num_self_play_games=args.num_games,
            self_play_seed=args.self_play_seed,
            self_play_black_agent=build_agent(args.black_agent),
            self_play_white_agent=build_agent(args.white_agent),
            episodes_output_path=str(output_dir / args.episodes_name),
            epochs=args.epochs,
            latest_checkpoint_path=str(output_dir / args.checkpoint_name),
            checkpoint_version=args.checkpoint_version,
            train_progress_callback=train_progress_callback,
        )
    except Exception as error:
        state_payload["session"]["status"] = "failed"
        state_payload["session"]["active_stage"] = "failed"
        state_payload["session"]["last_error"] = str(error)
        persist_state()
        raise

    summary = {
        "self_play": iteration_result.self_play_result.to_dict()["statistics"],
        "failures": iteration_result.self_play_result.failures,
        "written_episode_count": iteration_result.written_episode_count,
        "train_report": iteration_result.training_report.to_dict(),
    }
    latest_iteration = {
        "iteration": iteration_result.training_report.iteration,
        "samples": iteration_result.training_report.samples,
        "policy_loss": iteration_result.training_report.policy_loss,
        "value_loss": iteration_result.training_report.value_loss,
        "self_play_games": summary["self_play"]["total_games"],
        "self_play_failures": iteration_result.self_play_result.failures,
        "written_episode_count": iteration_result.written_episode_count,
        "promoted_tracks": iteration_result.training_report.promoted_tracks,
        "latest_checkpoint_path": iteration_result.training_report.latest_checkpoint_path,
        "completed_at": utc_timestamp(),
    }
    state_payload["latest_iteration"] = latest_iteration
    state_payload["history"] = ([latest_iteration] + preserved_history)[:10]
    state_payload["session"]["status"] = "completed"
    state_payload["session"]["active_stage"] = "completed"
    state_payload["session"]["current_iteration"] = iteration_result.training_report.iteration
    state_payload["session"]["latest_checkpoint_path"] = iteration_result.training_report.latest_checkpoint_path
    state_payload["session"]["last_error"] = None
    state_payload["epoch_tracking"]["target_epochs"] = args.epochs
    state_payload["epoch_tracking"]["current_epoch"] = args.epochs
    state_payload["epoch_tracking"]["current_epoch_progress_percent"] = 100
    state_payload["epoch_tracking"]["completed_epochs_after_run"] = iteration_result.training_report.total_epochs
    persist_state()

    summary_path = output_dir / args.summary_name
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
