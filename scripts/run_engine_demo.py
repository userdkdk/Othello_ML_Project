from __future__ import annotations

import argparse
from typing import Iterable

from engine import apply_move, create_new_game, get_valid_moves_for_current_player
from engine.types import CellState, Position


def render_board(board_strings: list[list[str]]) -> str:
    cell_to_char = {
        CellState.EMPTY.value: ".",
        CellState.BLACK.value: "B",
        CellState.WHITE.value: "W",
    }
    rows = []
    header = "  " + " ".join(str(col) for col in range(8))
    rows.append(header)
    for row_index, row in enumerate(board_strings):
        rendered = " ".join(cell_to_char[cell] for cell in row)
        rows.append(f"{row_index} {rendered}")
    return "\n".join(rows)


def parse_move(raw: str) -> Position:
    row_text, col_text = raw.split(",")
    return int(row_text), int(col_text)


def format_moves(moves: Iterable[Position]) -> str:
    return ", ".join(f"({row},{col})" for row, col in moves)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a simple Othello engine demo.")
    parser.add_argument(
        "--move",
        help="apply a single move in 'row,col' format, for example: --move 2,3",
    )
    args = parser.parse_args()

    state = create_new_game()

    print("Initial board")
    print(render_board(state.board.to_strings()))
    print(f"Current player: {state.current_player.value}")
    print(f"Valid moves: {format_moves(get_valid_moves_for_current_player(state))}")

    if args.move:
        position = parse_move(args.move)
        result = apply_move(state, position)
        print()
        print(f"Applied move: {position}")
        print(f"Success: {result.success}")
        print(f"Error: {result.error_code.value if result.error_code else None}")
        print(f"Flipped: {result.flipped_positions}")
        print(f"Next player: {state.current_player.value}")
        print(render_board(state.board.to_strings()))


if __name__ == "__main__":
    main()
