import json

import pytest

from training.episode_storage import EpisodeWriteError, write_episodes_jsonl
from training.heuristic_agent import HeuristicAgent
from training.match_runner import run_match
from training.random_agent import RandomAgent
from training.self_play_runner import run_self_play


def test_write_episodes_jsonl_writes_one_json_object_per_line(tmp_path):
    result = run_self_play(
        black_agent=RandomAgent(),
        white_agent=HeuristicAgent(),
        num_games=2,
        seed=23,
    )
    output_path = tmp_path / "episodes.jsonl"

    written_count = write_episodes_jsonl(output_path, result.episodes)

    lines = output_path.read_text(encoding="utf-8").splitlines()
    payloads = [json.loads(line) for line in lines]

    assert written_count == 2
    assert len(lines) == 2
    assert payloads[0]["episode_id"] == result.episodes[0].episode_id
    assert "encoded_state" not in payloads[0]["turns"][0]
    assert "valid_moves" in payloads[0]["turns"][0]
    assert "action_mask" in payloads[0]["turns"][0]


def test_write_episodes_jsonl_supports_append_mode(tmp_path):
    first = run_match(
        black_agent=RandomAgent(),
        white_agent=HeuristicAgent(),
        seed=31,
        episode_id="episode-first",
    ).episode
    second = run_match(
        black_agent=RandomAgent(),
        white_agent=HeuristicAgent(),
        seed=37,
        episode_id="episode-second",
    ).episode
    output_path = tmp_path / "episodes.jsonl"

    write_episodes_jsonl(output_path, [first], mode="w")
    write_episodes_jsonl(output_path, [second], mode="a")

    lines = output_path.read_text(encoding="utf-8").splitlines()
    payloads = [json.loads(line) for line in lines]

    assert [payload["episode_id"] for payload in payloads] == ["episode-first", "episode-second"]


def test_write_episodes_jsonl_returns_written_count_and_wraps_partial_failure(tmp_path):
    result = run_self_play(
        black_agent=RandomAgent(),
        white_agent=HeuristicAgent(),
        num_games=1,
        seed=41,
    )
    output_path = tmp_path / "episodes.jsonl"
    invalid_payload = {"episode_id": object()}

    with pytest.raises(EpisodeWriteError) as exc_info:
        write_episodes_jsonl(output_path, [result.episodes[0], invalid_payload])

    assert exc_info.value.written_count == 1
    lines = output_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1


def test_write_episodes_jsonl_rejects_unsupported_mode(tmp_path):
    output_path = tmp_path / "episodes.jsonl"

    with pytest.raises(ValueError):
        write_episodes_jsonl(output_path, [], mode="x")
