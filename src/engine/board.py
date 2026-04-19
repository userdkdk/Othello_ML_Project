from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from engine.types import CellState, Position


@dataclass
class Board:
    _matrix: list[list[CellState]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self._matrix:
            self._matrix = [[CellState.EMPTY for _ in range(8)] for _ in range(8)]
        if len(self._matrix) != 8 or any(len(row) != 8 for row in self._matrix):
            raise ValueError("board must be an 8x8 matrix")
        self._matrix = [
            [self._normalize_cell(cell) for cell in row]
            for row in self._matrix
        ]

    @staticmethod
    def _normalize_cell(cell: CellState | str) -> CellState:
        if isinstance(cell, CellState):
            return cell
        return CellState(cell)

    @classmethod
    def from_matrix(cls, matrix: Sequence[Sequence[CellState | str]]) -> "Board":
        return cls([[cls._normalize_cell(cell) for cell in row] for row in matrix])

    @classmethod
    def create_initial(cls) -> "Board":
        board = cls()
        board.set_cell((3, 3), CellState.WHITE)
        board.set_cell((3, 4), CellState.BLACK)
        board.set_cell((4, 3), CellState.BLACK)
        board.set_cell((4, 4), CellState.WHITE)
        return board

    def get_cell(self, position: Position) -> CellState:
        row, col = position
        if not self.is_in_bounds(position):
            raise IndexError(f"out of bounds: {position}")
        return self._matrix[row][col]

    def set_cell(self, position: Position, value: CellState) -> None:
        row, col = position
        if not self.is_in_bounds(position):
            raise IndexError(f"out of bounds: {position}")
        self._matrix[row][col] = value

    def is_in_bounds(self, position: Position) -> bool:
        row, col = position
        return 0 <= row < 8 and 0 <= col < 8

    def count_cells(self) -> dict[CellState, int]:
        counts = {state: 0 for state in CellState}
        for row in self._matrix:
            for cell in row:
                counts[cell] += 1
        return counts

    def clone(self) -> "Board":
        return Board([[cell for cell in row] for row in self._matrix])

    def to_matrix(self) -> list[list[CellState]]:
        return [[cell for cell in row] for row in self._matrix]

    def to_strings(self) -> list[list[str]]:
        return [[cell.value for cell in row] for row in self._matrix]
