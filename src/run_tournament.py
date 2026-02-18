#!/usr/bin/env python3
"""Run AI-vs-AI tournaments and log results to CSV.

Usage examples:
  python run_tournament.py --games 500 --out results.csv
  python run_tournament.py --games 200 --pairs "1,3;2,3" --out results.csv
"""
import csv
import time
import argparse
from collections import defaultdict

from src.tictactoe_engine import new_board, make_move_in_place, check_winner, is_tie, get_next_player, X, O

# Import AI modules
import Level1.ai_player as ai1
import Level2.start as ai2
import Level3.ai_level3 as ai3

AI_MODULES = {
    1: ai1,
    2: ai2,
    3: ai3,
}


def play_game(ai_X_module, ai_O_module, starting_player=X):
    board = new_board()
    current = starting_player
    moves = 0
    while True:
        if current == X:
            move = ai_X_module.get_move(board, X) if ai_X_module else None
        else:
            move = ai_O_module.get_move(board, O) if ai_O_module else None

        if move is None:
            # No moves available
            break

        made = make_move_in_place(board, move, current)
        moves += 1
        if not made:
            # Illegal move from AI; treat as loss for that AI
            winner = get_next_player(current)
            return winner, moves

        w = check_winner(board)
        if w is not None:
            return w, moves
        if is_tie(board):
            return 'Tie', moves

        current = get_next_player(current)


def run_pair(ai_level_X, ai_level_O, games, out_writer, start_player=X):
    mod_X = AI_MODULES[ai_level_X]
    mod_O = AI_MODULES[ai_level_O]

    for i in range(games):
        t0 = time.time()
        winner, moves = play_game(mod_X, mod_O, starting_player=start_player)
        duration = time.time() - t0
        # Normalize winner for CSV: 'X' or 'O' or 'Tie'
        out_writer.writerow({
            'ai_X_level': ai_level_X,
            'ai_O_level': ai_level_O,
            'starting_player': start_player,
            'winner': winner,
            'moves': moves,
            'duration_s': f"{duration:.6f}",
        })


def parse_pairs(s):
    # s like "1,2;1,3" -> [(1,2),(1,3)]
    pairs = []
    for part in s.split(';'):
        if not part.strip():
            continue
        a, b = part.split(',')
        pairs.append((int(a), int(b)))
    return pairs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--games', '-g', type=int, default=200, help='Games per pairing')
    parser.add_argument('--out', '-o', default='tourney_results.csv', help='CSV output file')
    parser.add_argument('--pairs', '-p', default=None, help='Pairs like "1,2;1,3"; if omitted run all pairs among 1..3')
    parser.add_argument('--start', choices=['X', 'O', 'alternate'], default='alternate')
    args = parser.parse_args()

    if args.pairs:
        pairs = parse_pairs(args.pairs)
    else:
        levels = sorted(AI_MODULES.keys())
        pairs = [(a, b) for a in levels for b in levels]

    with open(args.out, 'w', newline='') as f:
        fieldnames = ['ai_X_level', 'ai_O_level', 'starting_player', 'winner', 'moves', 'duration_s']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for (a, b) in pairs:
            # decide starting players
            if args.start == 'alternate':
                # run half with X start, half with O start
                half = args.games // 2
                print(f'Running {half} games: X(level={a}) start vs O(level={b})')
                run_pair(a, b, half, writer, start_player=X)
                print(f'Running {args.games - half} games: O(level={b}) start vs X(level={a})')
                run_pair(a, b, args.games - half, writer, start_player=O)
            else:
                sp = X if args.start == 'X' else O
                print(f'Running {args.games} games: start {args.start} for pairing {a} vs {b}')
                run_pair(a, b, args.games, writer, start_player=sp)

    print(f'Done. Results saved to {args.out}')


if __name__ == '__main__':
    main()
