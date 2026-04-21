from training.evaluator import Evaluator
from training.heuristic_agent import HeuristicAgent
from training.random_agent import RandomAgent
from training.match_runner import run_match
from training.self_play_runner import run_self_play
from training.trainer import Trainer


class InvalidPassAgent:
    name = "invalid-pass-agent"
    version = "invalid-pass-v1"

    def select_action(self, state, valid_moves, rng=None):
        return "PASS"


def test_self_play_returns_episodes_and_statistics():
    result = run_self_play(
        black_agent=RandomAgent(),
        white_agent=HeuristicAgent(),
        num_games=2,
        seed=3,
    )

    assert len(result.episodes) == 2
    assert result.statistics.total_games == 2
    assert result.failures == 0
    assert result.episodes[0].turns[0].policy_output is not None
    assert result.episodes[0].turns[0].policy_output["distribution_type"] == "full_action_space"
    assert result.to_dict()["statistics"]["total_games"] == 2


def test_trainer_and_evaluator_produce_reports():
    self_play_result = run_self_play(
        black_agent=RandomAgent(),
        white_agent=HeuristicAgent(),
        num_games=2,
        seed=11,
    )
    trainer_report = Trainer().train(self_play_result.episodes)
    evaluator_report = Evaluator().evaluate(
        black_agent=RandomAgent(),
        white_agent=HeuristicAgent(),
        num_games=2,
        seed=17,
    )

    assert trainer_report.completed_episodes == 2
    assert evaluator_report.games == 2
    assert 0.0 <= evaluator_report.black_win_rate <= 1.0
    assert trainer_report.to_dict()["completed_episodes"] == 2
    assert evaluator_report.to_dict()["games"] == 2


def test_evaluator_compare_agents_returns_balanced_side_metrics():
    report = Evaluator().compare_agents(
        candidate_agent=RandomAgent(version="candidate-v1"),
        opponent_agent=HeuristicAgent(version="opponent-v1"),
        num_games_per_side=2,
        seed=41,
    )

    assert report.games >= 0
    assert 0.0 <= report.black_side_win_rate <= 1.0
    assert 0.0 <= report.white_side_win_rate <= 1.0
    assert 0.0 <= report.balanced_eval_score <= 1.0
    assert report.candidate_black_games == 2
    assert report.candidate_white_games == 2


def test_run_self_play_excludes_failed_episodes_from_statistics():
    result = run_self_play(
        black_agent=InvalidPassAgent(),
        white_agent=HeuristicAgent(),
        num_games=2,
        seed=5,
    )

    assert len(result.episodes) == 2
    assert result.failures == 2
    assert result.statistics.total_games == 0
    assert result.episodes[0].failure is not None
    assert result.episodes[0].failure.failed_turn_index == 0
    assert result.to_dict()["failures"] == 2


def test_trainer_uses_episode_iterable_and_counts_completed_and_failed():
    self_play_result = run_self_play(
        black_agent=RandomAgent(),
        white_agent=HeuristicAgent(),
        num_games=2,
        seed=13,
    )
    failed_result = run_self_play(
        black_agent=InvalidPassAgent(),
        white_agent=HeuristicAgent(),
        num_games=1,
        seed=29,
    )
    episodes = (episode for episode in [*self_play_result.episodes, *failed_result.episodes])

    trainer_report = Trainer().train(episodes)

    assert trainer_report.completed_episodes == 2
    assert trainer_report.failed_episodes == 1
    assert trainer_report.average_turns > 0
    assert sum(trainer_report.reward_distribution.values()) == 2


def test_match_records_policy_versions_in_episode_metadata():
    result = run_match(
        black_agent=RandomAgent(version="random-black-v2"),
        white_agent=HeuristicAgent(version="heuristic-white-v3"),
        seed=19,
        episode_id="episode-policy-version",
    )

    assert result.episode.policy_black_version == "random-black-v2"
    assert result.episode.policy_white_version == "heuristic-white-v3"


def test_episode_to_dict_omits_encoded_state_but_keeps_policy_output():
    result = run_match(
        black_agent=RandomAgent(),
        white_agent=HeuristicAgent(),
        seed=7,
        episode_id="episode-serialization",
    )

    payload = result.episode.to_dict()
    first_turn = payload["turns"][0]

    assert "encoded_state" not in first_turn
    assert first_turn["policy_output"] is not None
