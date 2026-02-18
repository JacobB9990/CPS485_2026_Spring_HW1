import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tictactoe_engine import (
    available_moves,
    apply_move,
    is_legal_move,
    new_board,
    check_winner,
    is_tie,
    is_terminal,
    get_next_player,
    X,
    O,
    EMPTY,
)
import random


def find_winning_move(board, player):
    for m in available_moves(board):
        new_b = apply_move(board, m, player)
        if check_winner(new_b) == player:
            return m
    return None


# Heuristic AI for Level 2.
# Priority:
# 1. Win if possible
# 2. Block opponent's immediate win
# 3. Take center if available
# 4. Prefer corners
# 5. Otherwise pick a random available move
def get_move(board, player):
    moves = available_moves(board)
    if not moves:
        return None

    # 1) Win
    win = find_winning_move(board, player)
    if win:
        return win

    # 2) Block opponent
    opponent = get_next_player(player)
    block = find_winning_move(board, opponent)
    if block:
        return block

    # 3) Center
    center = (1, 1)
    if is_legal_move(board, center):
        return center

    # 4) Corners preference
    corners = [(0, 0), (0, 2), (2, 0), (2, 2)]
    available_corners = [c for c in corners if is_legal_move(board, c)]
    if available_corners:
        return random.choice(available_corners)

    # 5) Fallback to random edge or any move
    return random.choice(moves)


def print_board(board):
    def cell_str(v):
        return v if v is not None else "."

    for r in board:
        print(" ".join(cell_str(c) for c in r))


def human_move_prompt(board):
    while True:
        try:
            s = input("Enter your move as 'row,col' (0-2), or 'q' to quit: ")
            if s.strip().lower() == "q":
                return None
            parts = s.split(",")
            if len(parts) != 2:
                print("Invalid format. Use row,col")
                continue
            r = int(parts[0].strip())
            c = int(parts[1].strip())
            if not is_legal_move(board, (r, c)):
                print("Illegal move, try again")
                continue
            return (r, c)
        except Exception:
            print("Invalid input, try again")


if __name__ == "__main__":
    print("Level 2 Heuristic Tic-Tac-Toe")
    board = new_board()

    # Let human choose side
    human = None
    while human not in (X, O):
        choice = input(
            "Choose your symbol (X goes first). Enter X or O: ").strip().upper()
        if choice in ("X", "O"):
            human = choice

    ai = get_next_player(human)
    current = X

    while not is_terminal(board):
        print()
        print_board(board)
        if current == human:
            mv = human_move_prompt(board)
            if mv is None:
                print("Quitting. Goodbye!")
                break
            board = apply_move(board, mv, human)
        else:
            mv = get_move(board, ai)
            print(f"AI ({ai}) chooses: {mv}")
            board = apply_move(board, mv, ai)

        current = get_next_player(current)

    print()
    print_board(board)
    w = check_winner(board)
    if w:
        print(f"Winner: {w}")
    elif is_tie(board):
        print("Tie!")
