from engine.game_engine import create_new_game
from training.state_encoder import encode_state, encoded_state_shape


def test_encode_state_returns_four_planes_of_8x8():
    state = create_new_game()

    encoded = encode_state(state)

    assert encoded_state_shape(encoded) == {"planes": 4, "height": 8, "width": 8}
    assert encoded[0][3][4] == 1.0
    assert encoded[1][3][3] == 1.0
    assert encoded[2][0][0] == 1.0
