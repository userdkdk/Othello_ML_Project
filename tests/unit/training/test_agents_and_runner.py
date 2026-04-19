from training.heuristic_agent import HeuristicAgent
from training.match_runner import run_match
from training.random_agent import RandomAgent


def test_random_and_heuristic_agents_can_complete_match():
    result = run_match(
        black_agent=RandomAgent(),
        white_agent=HeuristicAgent(),
        seed=7,
        episode_id="episode-test",
    )

    assert result.episode.status == "completed"
    assert result.final_state.status.is_finished is True
    assert result.episode.final_reward in {1.0, 0.0, -1.0}
