import random
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tictactoe_engine import available_moves


def get_move(board, player):
    moves = available_moves(board)
    if not moves:
        return None
    return random.choice(moves)
