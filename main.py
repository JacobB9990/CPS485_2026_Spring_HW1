#!/usr/bin/env python3
"""Single entrypoint for running the project:

Subcommands:
  gui       Launch the pygame GUI
  tourney   Run AI-vs-AI tournaments and save CSV
  plot      Produce plots from a CSV

Examples:
  python main.py tourney --games 300 --out results.csv
  python main.py plot results.csv --out plots.png
  python main.py gui
"""
import argparse
import csv
import subprocess
import sys
import time
from collections import defaultdict
import math

import matplotlib.pyplot as plt

from src.tictactoe_engine import new_board, make_move_in_place, check_winner, is_tie, get_next_player, X, O
from src.Level1.ai_player import get_move as ai1_get_move
from src.Level2.start import get_move as ai2_get_move
from src.Level3.ai_level3 import get_move as ai3_get_move

AI_MODULES = {
    1: type('AI1', (), {'get_move': staticmethod(ai1_get_move)})(),
    2: type('AI2', (), {'get_move': staticmethod(ai2_get_move)})(),
    3: type('AI3', (), {'get_move': staticmethod(ai3_get_move)})(),
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
            break

        made = make_move_in_place(board, move, current)
        moves += 1
        if not made:
            winner = get_next_player(current)
            return winner, moves

        w = check_winner(board)
        if w is not None:
            return w, moves
        if is_tie(board):
            return 'Tie', moves

        current = get_next_player(current)


def run_tournament(pairs, games, out_path, start_mode='alternate'):
    with open(out_path, 'w', newline='') as f:
        fieldnames = ['ai_X_level', 'ai_O_level', 'starting_player', 'winner', 'moves', 'duration_s']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for (a, b) in pairs:
            if start_mode == 'alternate':
                half = games // 2
                _run_pair(a, b, half, writer, start_player=X)
                _run_pair(a, b, games - half, writer, start_player=O)
            else:
                sp = X if start_mode == 'X' else O
                _run_pair(a, b, games, writer, start_player=sp)


def _run_pair(ai_level_X, ai_level_O, games, writer, start_player=X):
    mod_X = AI_MODULES[ai_level_X]
    mod_O = AI_MODULES[ai_level_O]
    for i in range(games):
        t0 = time.time()
        winner, moves = play_game(mod_X, mod_O, starting_player=start_player)
        duration = time.time() - t0
        writer.writerow({
            'ai_X_level': ai_level_X,
            'ai_O_level': ai_level_O,
            'starting_player': start_player,
            'winner': winner,
            'moves': moves,
            'duration_s': f"{duration:.6f}",
        })


def load_results(path):
    rows = []
    with open(path, newline='') as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            rows.append(r)
    return rows


def improved_plots(csv_path, out_prefix='plots'):
    rows = load_results(csv_path)

    # Group by pairing
    pair_stats = defaultdict(lambda: {'X': 0, 'O': 0, 'Tie': 0, 'moves': []})
    for r in rows:
        aX = int(r['ai_X_level'])
        aO = int(r['ai_O_level'])
        key = (aX, aO)
        winner = r['winner']
        moves = int(r.get('moves', 0))
        pair_stats[key][winner] += 1
        pair_stats[key]['moves'].append(moves)

    # Build stacked bar chart per pairing (percentages)
    labels = []
    x_win = []
    o_win = []
    ties = []
    for k in sorted(pair_stats.keys()):
        stats = pair_stats[k]
        total = stats['X'] + stats['O'] + stats['Tie']
        if total == 0:
            continue
        labels.append(f"{k[0]}vs{k[1]}")
        x_win.append(stats['X'] / total * 100)
        o_win.append(stats['O'] / total * 100)
        ties.append(stats['Tie'] / total * 100)

    # Stacked bar
    fig, ax = plt.subplots(figsize=(10, 5))
    ind = list(range(len(labels)))
    p1 = ax.bar(ind, x_win, label='X wins', color='#4c72b0')
    p2 = ax.bar(ind, o_win, bottom=x_win, label='O wins', color='#dd8452')
    bottom_t = [x + y for x, y in zip(x_win, o_win)]
    p3 = ax.bar(ind, ties, bottom=bottom_t, label='Ties', color='#55a868')
    ax.set_ylabel('Percentage (%)')
    ax.set_title('Results by Pairing (X-level vs O-level)')
    ax.set_xticks(ind)
    ax.set_xticklabels(labels, rotation=45)
    ax.legend()
    plt.tight_layout()
    stacked_path = f"{out_prefix}_stacked.png"
    fig.savefig(stacked_path)

    # Boxplot of moves per pairing
    groups = []
    glabels = []
    for k in sorted(pair_stats.keys()):
        moves_list = pair_stats[k]['moves']
        if moves_list:
            groups.append(moves_list)
            glabels.append(f"{k[0]}vs{k[1]}")

    if groups:
        fig2, ax2 = plt.subplots(figsize=(10, 5))
        ax2.boxplot(groups, tick_labels=glabels, showmeans=True)
        ax2.set_ylabel('Moves per game')
        ax2.set_title('Distribution of Game Lengths by Pairing')
        plt.xticks(rotation=45)
        plt.tight_layout()
        box_path = f"{out_prefix}_moves_box.png"
        fig2.savefig(box_path)
    else:
        box_path = None

    print(f'Saved stacked bar to {stacked_path}')
    if box_path:
        print(f'Saved moves boxplot to {box_path}')


def cli():
    parser = argparse.ArgumentParser(prog='main.py')
    sub = parser.add_subparsers(dest='cmd')

    sub_gui = sub.add_parser('gui')
    sub_tourney = sub.add_parser('tourney')
    sub_tourney.add_argument('--games', '-g', type=int, default=200)
    sub_tourney.add_argument('--pairs', '-p', default=None,
                             help='Pairs like "1,2;1,3"; default all pairs among 1..3')
    sub_tourney.add_argument('--out', '-o', default='tourney_results.csv')
    sub_tourney.add_argument('--start', choices=['X', 'O', 'alternate'], default='alternate')

    sub_plot = sub.add_parser('plot')
    sub_plot.add_argument('csvfile')
    sub_plot.add_argument('--out', '-o', default='plots')

    args = parser.parse_args()
    if args.cmd is None:
        parser.print_help()
        sys.exit(1)

    if args.cmd == 'gui':
        subprocess.run([sys.executable, './src/tictactoe_pygame.py'])

    elif args.cmd == 'tourney':
        if args.pairs:
            pairs = []
            for part in args.pairs.split(';'):
                a, b = part.split(',')
                pairs.append((int(a), int(b)))
        else:
            levels = sorted(AI_MODULES.keys())
            pairs = [(a, b) for a in levels for b in levels]
        run_tournament(pairs, args.games, args.out, start_mode=args.start)
        print(f'Tournament finished -> {args.out}')

    elif args.cmd == 'plot':
        improved_plots(args.csvfile, out_prefix=args.out)


if __name__ == '__main__':
    cli()
