from __future__ import annotations

from dataclasses import dataclass, field
from os import PathLike
from typing import Any, Mapping, Optional

from training.agents import CNNPolicyAgent


@dataclass
class LoadedCNNCheckpoint:
    model: Any
    version: str
    model_kwargs: dict[str, Any] = field(default_factory=dict)
    optimizer_state_dict: Optional[dict[str, Any]] = None
    training_state: dict[str, Any] = field(default_factory=dict)
    evaluation_metadata: dict[str, Any] = field(default_factory=dict)
    track: Optional[str] = None
    raw_payload: Optional[dict[str, Any]] = None


def load_cnn_policy_agent(
    checkpoint_path: str | PathLike[str],
    *,
    device: str = "cpu",
    version: Optional[str] = None,
    model_kwargs: Optional[dict[str, Any]] = None,
) -> CNNPolicyAgent:
    loaded = load_cnn_checkpoint(
        checkpoint_path,
        device=device,
        version=version,
        model_kwargs=model_kwargs,
    )
    return CNNPolicyAgent(
        model=loaded.model,
        version=loaded.version,
        device=device,
    )


def load_cnn_checkpoint(
    checkpoint_path: str | PathLike[str],
    *,
    device: str = "cpu",
    version: Optional[str] = None,
    model_kwargs: Optional[dict[str, Any]] = None,
) -> LoadedCNNCheckpoint:
    import torch

    from training.cnn_model import CNNPolicyValueModel, MODEL_VERSION

    checkpoint = torch.load(checkpoint_path, map_location=device)
    state_dict, checkpoint_version, checkpoint_model_kwargs = _resolve_checkpoint_payload(checkpoint, torch)
    resolved_version = version or checkpoint_version or MODEL_VERSION
    resolved_model_kwargs = {
        **(checkpoint_model_kwargs or {}),
        **(model_kwargs or {}),
    }

    model = CNNPolicyValueModel(**resolved_model_kwargs)
    model.load_state_dict(state_dict)
    training_state = checkpoint.get("training_state") if isinstance(checkpoint, dict) else None
    optimizer_state_dict = checkpoint.get("optimizer_state_dict") if isinstance(checkpoint, dict) else None
    evaluation_metadata = {}
    track = None
    if isinstance(checkpoint, dict):
        for key in ("black_side_win_rate", "white_side_win_rate", "balanced_eval_score"):
            if key in checkpoint:
                evaluation_metadata[key] = checkpoint[key]
        track = checkpoint.get("track")
    return LoadedCNNCheckpoint(
        model=model,
        version=resolved_version,
        model_kwargs=resolved_model_kwargs,
        optimizer_state_dict=optimizer_state_dict,
        training_state=dict(training_state or {}),
        evaluation_metadata=evaluation_metadata,
        track=track,
        raw_payload=checkpoint if isinstance(checkpoint, dict) else None,
    )


def save_cnn_checkpoint(
    checkpoint_path: str | PathLike[str],
    model: Any,
    *,
    version: str,
    model_kwargs: Optional[dict[str, Any]] = None,
    checkpoint_format_version: str = "1",
    extra_metadata: Optional[Mapping[str, Any]] = None,
) -> None:
    import torch

    payload: dict[str, Any] = {
        "model_state_dict": model.state_dict(),
        "model_version": version,
        "checkpoint_format_version": checkpoint_format_version,
    }
    if model_kwargs:
        payload["model_kwargs"] = dict(model_kwargs)
    if extra_metadata:
        payload.update(dict(extra_metadata))
    torch.save(payload, checkpoint_path)


def _resolve_checkpoint_payload(checkpoint: Any, torch_module: Any) -> tuple[dict[str, Any], Optional[str], Optional[dict[str, Any]]]:
    if not isinstance(checkpoint, dict):
        raise TypeError(f"unsupported checkpoint payload type: {type(checkpoint)!r}")

    if "model_state_dict" in checkpoint:
        state_dict = checkpoint["model_state_dict"]
        return state_dict, checkpoint.get("model_version"), checkpoint.get("model_kwargs")

    if "state_dict" in checkpoint:
        state_dict = checkpoint["state_dict"]
        return state_dict, checkpoint.get("model_version"), checkpoint.get("model_kwargs")

    if _is_state_dict_payload(checkpoint, torch_module):
        return checkpoint, None, None

    raise ValueError("checkpoint payload does not contain a supported state dict")


def _is_state_dict_payload(payload: Mapping[str, Any], torch_module: Any) -> bool:
    if not payload:
        return False
    tensor_types = (torch_module.Tensor,)
    return all(isinstance(value, tensor_types) for value in payload.values())


__all__ = ["CNNPolicyAgent", "LoadedCNNCheckpoint", "load_cnn_checkpoint", "load_cnn_policy_agent", "save_cnn_checkpoint"]
