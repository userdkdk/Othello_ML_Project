from training.evaluator import Evaluator
from training.heuristic_agent import HeuristicAgent
from training.random_agent import RandomAgent
from training.self_play_runner import run_self_play
from training.trainer import Trainer


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
