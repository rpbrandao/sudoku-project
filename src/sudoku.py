"""
src/sudoku.py
Core Sudoku game model — board, cells, validation, hints.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


# ──────────────────────────────────────────────
# Cell
# ──────────────────────────────────────────────

@dataclass
class Cell:
    col: int
    row: int
    value: int          # 0 = empty
    fixed: bool         # True = pre-filled, cannot be changed

    def is_empty(self) -> bool:
        return self.value == 0

    def __repr__(self) -> str:
        return f"Cell({self.col},{self.row},{self.value},{'fixed' if self.fixed else 'editable'})"


# ──────────────────────────────────────────────
# Board
# ──────────────────────────────────────────────

class SudokuBoard:
    """
    9×9 Sudoku board.

    Coordinate system: col (x, 0-8) and row (y, 0-8).
    grid[row][col] gives the Cell at that position.
    """

    SIZE = 9
    BOX  = 3

    def __init__(self):
        self.grid: list[list[Cell]] = [
            [Cell(col, row, 0, False) for col in range(self.SIZE)]
            for row in range(self.SIZE)
        ]
        # Store the solved board for hints
        self._solution: Optional[list[list[int]]] = None

    # ──────────────────────────────────────────
    # Parsing
    # ──────────────────────────────────────────

    @classmethod
    def from_args(cls, args_string: str) -> "SudokuBoard":
        """
        Build a board from the DIO argument format.

        Each token: "col,row;value,fixed"
        Example: "0,0;4,false 2,0;9,true"
        """
        board = cls()
        for token in args_string.strip().split():
            token = token.strip()
            if not token:
                continue
            try:
                pos_part, val_part = token.split(";")
                col, row = map(int, pos_part.split(","))
                value_str, fixed_str = val_part.split(",")
                value = int(value_str)
                fixed = fixed_str.strip().lower() == "true"
                board.grid[row][col] = Cell(col, row, value, fixed)
            except (ValueError, IndexError) as e:
                raise ValueError(f"Invalid token '{token}': {e}") from e

        board._solution = board._solve_copy()
        return board

    @classmethod
    def from_grid(cls, numbers: list[list[int]]) -> "SudokuBoard":
        """Build a board from a simple 9×9 list of ints (0 = empty)."""
        board = cls()
        for row in range(cls.SIZE):
            for col in range(cls.SIZE):
                v = numbers[row][col]
                board.grid[row][col] = Cell(col, row, v, v != 0)
        board._solution = board._solve_copy()
        return board

    # ──────────────────────────────────────────
    # Cell access
    # ──────────────────────────────────────────

    def get(self, col: int, row: int) -> Cell:
        return self.grid[row][col]

    def set_value(self, col: int, row: int, value: int) -> bool:
        """
        Set a cell value. Returns True if the move is allowed.
        Raises ValueError if cell is fixed or value out of range.
        """
        cell = self.get(col, row)
        if cell.fixed:
            raise ValueError(f"Cell ({col},{row}) is fixed and cannot be changed.")
        if not (0 <= value <= self.SIZE):
            raise ValueError(f"Value must be 0–{self.SIZE}, got {value}.")
        cell.value = value
        return True

    # ──────────────────────────────────────────
    # Validation
    # ──────────────────────────────────────────

    def is_valid_move(self, col: int, row: int, value: int) -> bool:
        """Check if placing value at (col, row) is valid per Sudoku rules."""
        if value == 0:
            return True  # clearing is always valid

        # Check row
        for c in range(self.SIZE):
            if c != col and self.grid[row][c].value == value:
                return False

        # Check column
        for r in range(self.SIZE):
            if r != row and self.grid[r][col].value == value:
                return False

        # Check 3×3 box
        box_col = (col // self.BOX) * self.BOX
        box_row = (row // self.BOX) * self.BOX
        for r in range(box_row, box_row + self.BOX):
            for c in range(box_col, box_col + self.BOX):
                if (c != col or r != row) and self.grid[r][c].value == value:
                    return False

        return True

    def get_conflicts(self, col: int, row: int) -> list[tuple[int, int]]:
        """Return list of (col, row) cells that conflict with the given cell."""
        value = self.get(col, row).value
        if value == 0:
            return []
        conflicts = []
        for c in range(self.SIZE):
            if c != col and self.grid[row][c].value == value:
                conflicts.append((c, row))
        for r in range(self.SIZE):
            if r != row and self.grid[r][col].value == value:
                conflicts.append((col, r))
        box_col = (col // self.BOX) * self.BOX
        box_row = (row // self.BOX) * self.BOX
        for r in range(box_row, box_row + self.BOX):
            for c in range(box_col, box_col + self.BOX):
                if (c != col or r != row) and self.grid[r][c].value == value:
                    conflicts.append((c, r))
        return list(set(conflicts))

    def is_complete(self) -> bool:
        """Return True if the board is fully and correctly filled."""
        for row in range(self.SIZE):
            for col in range(self.SIZE):
                cell = self.grid[row][col]
                if cell.value == 0:
                    return False
                if not self.is_valid_move(col, row, cell.value):
                    return False
        return True

    # ──────────────────────────────────────────
    # Solver (backtracking)
    # ──────────────────────────────────────────

    def _solve_copy(self) -> Optional[list[list[int]]]:
        """Return a solved copy of the current grid, or None if unsolvable."""
        nums = [[self.grid[r][c].value for c in range(self.SIZE)]
                for r in range(self.SIZE)]
        if self._backtrack(nums):
            return nums
        return None

    def _backtrack(self, nums: list[list[int]]) -> bool:
        for row in range(self.SIZE):
            for col in range(self.SIZE):
                if nums[row][col] == 0:
                    for v in range(1, self.SIZE + 1):
                        if self._valid_in_grid(nums, col, row, v):
                            nums[row][col] = v
                            if self._backtrack(nums):
                                return True
                            nums[row][col] = 0
                    return False
        return True

    def _valid_in_grid(self, nums: list[list[int]], col: int, row: int, v: int) -> bool:
        if v in nums[row]:
            return False
        if v in [nums[r][col] for r in range(self.SIZE)]:
            return False
        bc, br = (col // self.BOX) * self.BOX, (row // self.BOX) * self.BOX
        for r in range(br, br + self.BOX):
            for c in range(bc, bc + self.BOX):
                if nums[r][c] == v:
                    return False
        return True

    # ──────────────────────────────────────────
    # Hint
    # ──────────────────────────────────────────

    def get_hint(self) -> Optional[tuple[int, int, int]]:
        """
        Return (col, row, value) for one empty cell from the solution.
        Returns None if no solution or board is already complete.
        """
        if not self._solution:
            return None
        for row in range(self.SIZE):
            for col in range(self.SIZE):
                if self.grid[row][col].value == 0:
                    return col, row, self._solution[row][col]
        return None

    # ──────────────────────────────────────────
    # Display
    # ──────────────────────────────────────────

    def to_string(self) -> str:
        lines = []
        for row in range(self.SIZE):
            if row % 3 == 0 and row != 0:
                lines.append("------+-------+------")
            row_chars = []
            for col in range(self.SIZE):
                if col % 3 == 0 and col != 0:
                    row_chars.append("|")
                v = self.grid[row][col].value
                row_chars.append(str(v) if v != 0 else ".")
            lines.append(" ".join(row_chars))
        return "\n".join(lines)
