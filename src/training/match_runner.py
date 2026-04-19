from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Dict, Optional

from engine.game_engine import (
    apply_move,
    create_new_game,
    get_valid_moves_for_current_player,
    pass_turn,
)
from engine.types import GameState, Player
from training.action_mask import build_action_mask
from training.agents import Agent
from training.episode import Episode, TurnRecord
from training.state_encoder import encode_state


@dataclass
class MatchResult:
    final_state: GameState
    episode: Episode
    move_count: int
    pass_count: int


def run_match(
    black_agent: Agent,
    white_agent: Agent,
    seed: int,
    episode_id: str,
) -> MatchResult:
    state = create_new_game()
    episode = Episode(
        episode_id=episode_id,
        seed=seed,
        policy_black_version=black_agent.version,
        policy_white_version=white_agent.version,
    )
    rng = Random(seed)
    pass_count = 0

    while not state.status.is_finished:
        valid_moves = get_valid_moves_for_current_player(state)
        acting_agent = black_agent if state.current_player == Player.BLACK else white_agent
        action = acting_agent.select_action(state.clone(), valid_moves, rng)
        encoded_state = encode_state(state)
        action_mask = build_action_mask(valid_moves)

        turn = TurnRecord(
            turn_index=len(episode.turns),
            player=state.current_player,
            state=state.to_dict(),
            action=action,
            valid_moves=list(valid_moves),
            action_mask=action_mask,
            encoded_state=encoded_state,
            policy_output=None,
        )
        episode.turns.append(turn)

        if action == "PASS":
            result = pass_turn(state)
            pass_count += 1 if result.success else 0
        else:
            result = apply_move(state, action)

        if not result.success:
            episode.mark_failed(
                error_code=result.error_code.value if result.error_code else "UNKNOWN",
                message="agent produced an invalid action",
                failed_turn_index=turn.turn_index,
            )
            return MatchResult(
                final_state=state,
                episode=episode,
                move_count=len([t for t in episode.turns if t.action != "PASS"]),
                pass_count=pass_count,
            )

    episode.finalize(state.status.winner)
    return MatchResult(
        final_state=state,
        episode=episode,
        move_count=len([t for t in episode.turns if t.action != "PASS"]),
        pass_count=pass_count,
    )
