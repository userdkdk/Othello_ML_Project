from training.action_mask import ACTION_SPACE_SIZE, PASS_INDEX, action_to_index, build_action_mask, index_to_action


def test_action_index_round_trip_for_board_move_and_pass():
    assert action_to_index((2, 3)) == 19
    assert index_to_action(19) == (2, 3)
    assert action_to_index("PASS") == PASS_INDEX
    assert index_to_action(PASS_INDEX) == "PASS"


def test_build_action_mask_marks_valid_moves_or_pass():
    mask = build_action_mask([(2, 3), (5, 4)])
    assert len(mask) == ACTION_SPACE_SIZE
    assert mask[action_to_index((2, 3))] == 1
    assert mask[action_to_index((5, 4))] == 1
    assert mask[PASS_INDEX] == 0

    pass_mask = build_action_mask([])
    assert pass_mask[PASS_INDEX] == 1
