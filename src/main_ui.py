"""
src/main_ui.py
Sudoku — graphical interface (branch ui) using Tkinter.

Usage:
    python src/main_ui.py
"""

import sys
import os
import time
import tkinter as tk
from tkinter import messagebox, font

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from src.sudoku import SudokuBoard

DEFAULT_ARGS = (
    "0,0;4,false 1,0;7,false 2,0;9,true 3,0;5,false 4,0;8,true 5,0;6,true 6,0;2,true 7,0;3,false 8,0;1,false "
    "0,1;1,false 1,1;3,true 2,1;5,false 3,1;4,false 4,1;7,true 5,1;2,false 6,1;8,false 7,1;9,true 8,1;6,true "
    "0,2;2,false 1,2;6,true 2,2;8,false 3,2;9,false 4,2;1,true 5,2;3,false 6,2;7,false 7,2;4,false 8,2;5,true "
    "0,3;5,true 1,3;1,false 2,3;3,true 3,3;7,false 4,3;6,false 5,3;4,false 6,3;9,false 7,3;8,true 8,3;2,false "
    "0,4;8,false 1,4;9,true 2,4;7,false 3,4;1,true 4,4;2,true 5,4;5,true 6,4;3,false 7,4;6,true 8,4;4,false "
    "0,5;6,false 1,5;4,true 2,5;2,false 3,5;3,false 4,5;9,false 5,5;8,false 6,5;1,true 7,5;5,false 8,5;7,true "
    "0,6;7,true 1,6;5,false 2,6;4,false 3,6;2,false 4,6;3,true 5,6;9,false 6,6;6,false 7,6;1,true 8,6;8,false "
    "0,7;9,true 1,7;8,true 2,7;1,false 3,7;6,false 4,7;4,true 5,7;7,false 6,7;5,false 7,7;2,true 8,7;3,false "
    "0,8;3,false 1,8;2,false 2,8;6,true 3,8;8,true 4,8;5,true 5,8;1,false 6,8;4,true 7,8;7,false 8,8;9,false"
)

# ── Color palette ──
C_BG          = "#1E1E2E"
C_PANEL       = "#2A2A3E"
C_CELL_NORM   = "#2A2A3E"
C_CELL_SEL    = "#3D3D5C"
C_CELL_HINT   = "#1E3A2F"
C_CELL_ERR    = "#3A1E1E"
C_CELL_FIXED  = "#252535"
C_BOX_LINE    = "#7C7CAA"
C_CELL_LINE   = "#3A3A5C"
C_TXT_FIXED   = "#9999CC"
C_TXT_USER    = "#66EE88"
C_TXT_ERR     = "#EE4444"
C_TXT_HINT    = "#44CCAA"
C_ACCENT      = "#7C7CDD"
C_BTN         = "#3D3D6C"
C_BTN_HOV     = "#5555AA"
C_WHITE       = "#E0E0FF"
C_MUTED       = "#888899"

CELL_SIZE     = 56
MARGIN        = 20
BOARD_SIZE    = CELL_SIZE * 9 + MARGIN * 2
CANVAS_W      = BOARD_SIZE
CANVAS_H      = BOARD_SIZE


class SudokuUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Sudoku")
        self.root.configure(bg=C_BG)
        self.root.resizable(False, False)

        self.board = SudokuBoard.from_args(DEFAULT_ARGS)
        self._initial_args = DEFAULT_ARGS

        self.selected: tuple[int, int] | None = None   # (col, row)
        self.hint_cells: set[tuple[int, int]] = set()
        self.error_cells: set[tuple[int, int]] = set()

        self._start_time = time.time()
        self._timer_running = True

        self._build_ui()
        self._draw_board()
        self._tick_timer()

    # ──────────────────────────────────────────
    # UI construction
    # ──────────────────────────────────────────

    def _build_ui(self):
        # Title
        title_frame = tk.Frame(self.root, bg=C_BG)
        title_frame.pack(pady=(16, 4))
        tk.Label(
            title_frame, text="SUDOKU",
            bg=C_BG, fg=C_ACCENT,
            font=("Courier", 28, "bold")
        ).pack()

        # Timer
        self.timer_var = tk.StringVar(value="00:00")
        tk.Label(
            title_frame, textvariable=self.timer_var,
            bg=C_BG, fg=C_MUTED,
            font=("Courier", 14)
        ).pack()

        # Canvas
        canvas_frame = tk.Frame(self.root, bg=C_BG)
        canvas_frame.pack(padx=20)

        self.canvas = tk.Canvas(
            canvas_frame,
            width=CANVAS_W, height=CANVAS_H,
            bg=C_BG, highlightthickness=0
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self._on_click)
        self.root.bind("<Key>", self._on_key)

        # Buttons
        btn_frame = tk.Frame(self.root, bg=C_BG)
        btn_frame.pack(pady=16, padx=20, fill="x")

        buttons = [
            ("Dica",     self._on_hint),
            ("Verificar",self._on_check),
            ("Limpar",   self._on_clear),
            ("Novo Jogo",self._on_new_game),
        ]
        for label, cmd in buttons:
            btn = tk.Button(
                btn_frame, text=label, command=cmd,
                bg=C_BTN, fg=C_WHITE,
                activebackground=C_BTN_HOV, activeforeground=C_WHITE,
                relief="flat", bd=0,
                font=("Courier", 11, "bold"),
                padx=14, pady=8, cursor="hand2"
            )
            btn.pack(side="left", expand=True, fill="x", padx=4)

        # Status bar
        self.status_var = tk.StringVar(value="Select a cell and type a number")
        tk.Label(
            self.root, textvariable=self.status_var,
            bg=C_BG, fg=C_MUTED,
            font=("Courier", 10),
            pady=8
        ).pack()

    # ──────────────────────────────────────────
    # Drawing
    # ──────────────────────────────────────────

    def _cell_rect(self, col: int, row: int) -> tuple[int, int, int, int]:
        x1 = MARGIN + col * CELL_SIZE
        y1 = MARGIN + row * CELL_SIZE
        return x1, y1, x1 + CELL_SIZE, y1 + CELL_SIZE

    def _draw_board(self):
        self.canvas.delete("all")
        for row in range(9):
            for col in range(9):
                self._draw_cell(col, row)
        self._draw_grid_lines()

    def _cell_bg(self, col: int, row: int) -> str:
        if (col, row) in self.error_cells:
            return C_CELL_ERR
        if (col, row) in self.hint_cells:
            return C_CELL_HINT
        if self.selected == (col, row):
            return C_CELL_SEL
        cell = self.board.get(col, row)
        if cell.fixed:
            return C_CELL_FIXED
        # Highlight same row/col/box as selection
        if self.selected:
            sc, sr = self.selected
            bc_s, br_s = (sc // 3) * 3, (sr // 3) * 3
            bc_c, br_c = (col // 3) * 3, (row // 3) * 3
            if row == sr or col == sc or (bc_c == bc_s and br_c == br_s):
                return "#252540"
        return C_CELL_NORM

    def _draw_cell(self, col: int, row: int):
        x1, y1, x2, y2 = self._cell_rect(col, row)
        bg = self._cell_bg(col, row)
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=bg, outline="")

        cell = self.board.get(col, row)
        if cell.value != 0:
            if (col, row) in self.error_cells:
                color = C_TXT_ERR
            elif (col, row) in self.hint_cells:
                color = C_TXT_HINT
            elif cell.fixed:
                color = C_TXT_FIXED
            else:
                color = C_TXT_USER

            weight = "bold" if cell.fixed else "normal"
            self.canvas.create_text(
                (x1 + x2) // 2, (y1 + y2) // 2,
                text=str(cell.value),
                fill=color,
                font=("Courier", 20, weight),
            )

    def _draw_grid_lines(self):
        for i in range(10):
            x = MARGIN + i * CELL_SIZE
            y = MARGIN + i * CELL_SIZE
            width = 2.5 if i % 3 == 0 else 0.5
            color = C_BOX_LINE if i % 3 == 0 else C_CELL_LINE
            self.canvas.create_line(x, MARGIN, x, MARGIN + 9 * CELL_SIZE,
                                    fill=color, width=width)
            self.canvas.create_line(MARGIN, y, MARGIN + 9 * CELL_SIZE, y,
                                    fill=color, width=width)

    # ──────────────────────────────────────────
    # Events
    # ──────────────────────────────────────────

    def _on_click(self, event):
        col = (event.x - MARGIN) // CELL_SIZE
        row = (event.y - MARGIN) // CELL_SIZE
        if 0 <= col < 9 and 0 <= row < 9:
            self.selected = (col, row)
            self.hint_cells.discard((col, row))
            self._update_errors()
            self._draw_board()

    def _on_key(self, event):
        if not self.selected:
            return
        col, row = self.selected

        # Arrow key navigation
        moves = {"Up": (0,-1), "Down": (0,1), "Left": (-1,0), "Right": (1,0)}
        if event.keysym in moves:
            dc, dr = moves[event.keysym]
            nc, nr = col + dc, row + dr
            if 0 <= nc < 9 and 0 <= nr < 9:
                self.selected = (nc, nr)
                self._draw_board()
            return

        # Delete / backspace = clear
        if event.keysym in ("Delete", "BackSpace"):
            cell = self.board.get(col, row)
            if not cell.fixed:
                try:
                    self.board.set_value(col, row, 0)
                    self.error_cells.discard((col, row))
                    self.hint_cells.discard((col, row))
                    self._update_errors()
                    self._draw_board()
                    self.status_var.set(f"Cell ({col+1},{row+1}) cleared")
                except ValueError:
                    pass
            return

        # Digit input
        if event.char.isdigit() and event.char != "0":
            val = int(event.char)
            cell = self.board.get(col, row)
            if cell.fixed:
                self.status_var.set("This cell is fixed and cannot be changed.")
                return
            if not self.board.is_valid_move(col, row, val):
                # Place it but mark as error
                cell.value = val
                self._update_errors()
                self._draw_board()
                self.status_var.set(f"⚠ Conflict detected at ({col+1},{row+1})!")
                return
            try:
                self.board.set_value(col, row, val)
                self.error_cells.discard((col, row))
                self.hint_cells.discard((col, row))
                self._update_errors()
                self._draw_board()
                self.status_var.set(f"Placed {val} at ({col+1},{row+1})")
                if self.board.is_complete():
                    self._on_win()
            except ValueError as e:
                self.status_var.set(str(e))

    def _update_errors(self):
        self.error_cells.clear()
        for row in range(9):
            for col in range(9):
                cell = self.board.get(col, row)
                if cell.value != 0 and not self.board.is_valid_move(col, row, cell.value):
                    self.error_cells.add((col, row))
                    for cc, cr in self.board.get_conflicts(col, row):
                        self.error_cells.add((cc, cr))

    # ──────────────────────────────────────────
    # Button actions
    # ──────────────────────────────────────────

    def _on_hint(self):
        hint = self.board.get_hint()
        if hint:
            col, row, val = hint
            self.board.set_value(col, row, val)
            self.hint_cells.add((col, row))
            self.selected = (col, row)
            self._update_errors()
            self._draw_board()
            self.status_var.set(f"Hint: placed {val} at ({col+1},{row+1})")
        else:
            self.status_var.set("No hints available — board may be complete!")

    def _on_check(self):
        self._update_errors()
        self._draw_board()
        if self.board.is_complete():
            self._on_win()
        elif self.error_cells:
            self.status_var.set(f"Found {len(self.error_cells)} conflicting cells — highlighted in red.")
        else:
            empties = sum(
                1 for r in range(9) for c in range(9)
                if self.board.get(c, r).value == 0
            )
            self.status_var.set(f"No errors so far! {empties} empty cells remaining.")

    def _on_clear(self):
        for r in range(9):
            for c in range(9):
                cell = self.board.get(c, r)
                if not cell.fixed:
                    cell.value = 0
        self.error_cells.clear()
        self.hint_cells.clear()
        self.selected = None
        self._draw_board()
        self.status_var.set("Board cleared — only fixed cells remain.")

    def _on_new_game(self):
        self.board = SudokuBoard.from_args(self._initial_args)
        self.selected = None
        self.error_cells.clear()
        self.hint_cells.clear()
        self._start_time = time.time()
        self._timer_running = True
        self._draw_board()
        self.status_var.set("New game started!")

    def _on_win(self):
        self._timer_running = False
        elapsed = int(time.time() - self._start_time)
        m, s = divmod(elapsed, 60)
        self.status_var.set(f"🎉 Solved! Time: {m:02d}:{s:02d}")
        messagebox.showinfo(
            "Sudoku",
            f"🎉 Congratulations!\n\nYou solved the puzzle in {m:02d}:{s:02d}!"
        )

    # ──────────────────────────────────────────
    # Timer
    # ──────────────────────────────────────────

    def _tick_timer(self):
        if self._timer_running:
            elapsed = int(time.time() - self._start_time)
            m, s = divmod(elapsed, 60)
            self.timer_var.set(f"{m:02d}:{s:02d}")
        self.root.after(1000, self._tick_timer)


def main():
    root = tk.Tk()
    app = SudokuUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
