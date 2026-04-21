from training.action_mask import ACTION_SPACE_SIZE, PASS_INDEX, action_to_index, build_action_mask, index_to_action
from training.agents import CNNPolicyAgent, HeuristicAgent, RandomAgent
from training.cnn_policy_agent import LoadedCNNCheckpoint, load_cnn_checkpoint, load_cnn_policy_agent, save_cnn_checkpoint
from training.episode import Episode, TurnRecord
from training.episode_storage import EpisodeWriteError, write_episodes_jsonl
from training.evaluator import EvaluationReport, Evaluator
from training.match_runner import MatchResult, run_match
from training.policy_client import PolicyClient, PolicyOutput, policy_output_to_dict
from training.self_play_runner import SelfPlayResult, run_self_play
from training.state_encoder import encode_state
from training.statistics import MatchStatistics
from training.training_pipeline import PolicyTrainingIterationResult, PolicyTrainingPipeline
from training.trainer import ModelTrainingReport, PolicyValueTrainer, Trainer, TrainingReport

try:
    from training.cnn_model import CNNPolicyValueModel, MODEL_VERSION
except ModuleNotFoundError:  # pragma: no cover - local env may not include torch
    CNNPolicyValueModel = None
    MODEL_VERSION = None

__all__ = [
    "ACTION_SPACE_SIZE",
    "CNNPolicyValueModel",
    "CNNPolicyAgent",
    "LoadedCNNCheckpoint",
    "PASS_INDEX",
    "Episode",
    "EpisodeWriteError",
    "EvaluationReport",
    "Evaluator",
    "HeuristicAgent",
    "MatchResult",
    "MatchStatistics",
    "MODEL_VERSION",
    "ModelTrainingReport",
    "PolicyClient",
    "PolicyOutput",
    "PolicyTrainingIterationResult",
    "PolicyTrainingPipeline",
    "policy_output_to_dict",
    "RandomAgent",
    "PolicyValueTrainer",
    "save_cnn_checkpoint",
    "load_cnn_checkpoint",
    "SelfPlayResult",
    "Trainer",
    "TrainingReport",
    "TurnRecord",
    "action_to_index",
    "build_action_mask",
    "encode_state",
    "index_to_action",
    "load_cnn_policy_agent",
    "run_match",
    "run_self_play",
    "write_episodes_jsonl",
]
