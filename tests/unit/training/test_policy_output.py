from engine.game_engine import create_new_game
from training.policy_client import PolicyClient, policy_output_to_dict


def test_agent_policy_output_is_serialized_into_turn_records_shape():
    state = create_new_game()
    valid_moves = [(2, 3), (3, 2), (4, 5), (5, 4)]

    output = PolicyClient().predict(state, valid_moves)
    payload = policy_output_to_dict(output)

    assert payload["distribution_type"] == "full_action_space"
    assert payload["selected_action"]["kind"] == "MOVE"
    assert payload["selected_action"]["position"] is not None
    assert "PASS" not in payload["action_probabilities"]
