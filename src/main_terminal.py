"""
src/main_terminal.py
Sudoku — terminal version (branch main).

Usage:
    python src/main_terminal.py
    python src/main_terminal.py "0,0;4,false 1,0;7,false ..."
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from src.sudoku import SudokuBoard

# Default puzzle from DIO
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

CYAN   = "\033[96m"
YELLOW = "\033[93m"
GREEN  = "\033[92m"
RED    = "\033[91m"
BOLD   = "\033[1m"
RESET  = "\033[0m"


def print_board(board: SudokuBoard):
    print()
    print(f"  {BOLD}  1 2 3   4 5 6   7 8 9{RESET}")
    print(f"  +-------+-------+-------+")
    for row in range(9):
        if row > 0 and row % 3 == 0:
            print(f"  +-------+-------+-------+")
        line = f"{row+1} |"
        for col in range(9):
            if col > 0 and col % 3 == 0:
                line += " |"
            cell = board.get(col, row)
            if cell.value == 0:
                line += f" {YELLOW}.{RESET}"
            elif cell.fixed:
                line += f" {CYAN}{BOLD}{cell.value}{RESET}"
            else:
                line += f" {GREEN}{cell.value}{RESET}"
        line += " |"
        print(line)
    print(f"  +-------+-------+-------+")
    print()
    print(f"  {CYAN}{BOLD}Blue{RESET} = fixed  {GREEN}Green{RESET} = your answer  {YELLOW}.{RESET} = empty")
    print()


def print_banner():
    print(f"""
{BOLD}{CYAN}
  ╔═══════════════════════════════╗
  ║     S U D O K U  🔢           ║
  ║     Terminal Edition          ║
  ╚═══════════════════════════════╝
{RESET}
  Commands:
  {BOLD}row col value{RESET}  — place a number (e.g. 1 1 5)
  {BOLD}hint{RESET}           — get a hint for one empty cell
  {BOLD}check{RESET}          — check if current board is correct
  {BOLD}reset{RESET}          — reset all non-fixed cells
  {BOLD}quit{RESET}           — exit the game
""")


def main():
    args_string = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_ARGS

    try:
        board = SudokuBoard.from_args(args_string)
    except ValueError as e:
        print(f"{RED}Error parsing board: {e}{RESET}")
        sys.exit(1)

    print_banner()
    print_board(board)

    while True:
        try:
            raw = input(f"{BOLD}> {RESET}").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{GREEN}Thanks for playing! Goodbye.{RESET}")
            break

        if not raw:
            continue

        if raw == "quit":
            print(f"{GREEN}Thanks for playing! Goodbye.{RESET}")
            break

        elif raw == "hint":
            hint = board.get_hint()
            if hint:
                col, row, val = hint
                print(f"{YELLOW}Hint: row {row+1}, col {col+1} → {val}{RESET}")
            else:
                print(f"{RED}No hints available.{RESET}")

        elif raw == "check":
            if board.is_complete():
                print(f"\n{GREEN}{BOLD}🎉 Congratulations! Puzzle solved correctly!{RESET}\n")
                break
            else:
                # Count empties
                empties = sum(
                    1 for r in range(9) for c in range(9)
                    if board.get(c, r).value == 0
                )
                print(f"{YELLOW}Not complete yet — {empties} empty cells remaining.{RESET}")

        elif raw == "reset":
            for r in range(9):
                for c in range(9):
                    cell = board.get(c, r)
                    if not cell.fixed:
                        cell.value = 0
            print(f"{YELLOW}Board reset to initial state.{RESET}")
            print_board(board)

        else:
            parts = raw.split()
            if len(parts) != 3:
                print(f"{RED}Usage: row col value  (e.g. 1 1 5){RESET}")
                continue
            try:
                row_in, col_in, val_in = int(parts[0]), int(parts[1]), int(parts[2])
            except ValueError:
                print(f"{RED}Please enter integers only.{RESET}")
                continue

            if not (1 <= row_in <= 9 and 1 <= col_in <= 9 and 1 <= val_in <= 9):
                print(f"{RED}Row, col, and value must be between 1 and 9.{RESET}")
                continue

            col = col_in - 1
            row = row_in - 1

            try:
                if not board.is_valid_move(col, row, val_in):
                    print(f"{RED}Invalid move! {val_in} conflicts with existing values.{RESET}")
                    continue
                board.set_value(col, row, val_in)
                print_board(board)

                if board.is_complete():
                    print(f"{GREEN}{BOLD}🎉 Puzzle complete! Well done!{RESET}\n")
                    break

            except ValueError as e:
                print(f"{RED}{e}{RESET}")


if __name__ == "__main__":
    main()
