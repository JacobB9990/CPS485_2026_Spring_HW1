#!/usr/bin/env python3
"""Plot tournament results saved by run_tournament.py

Usage:
  python plot_stats.py tourney_results.csv
"""
import sys
import csv
from collections import defaultdict
import matplotlib.pyplot as plt


def load_results(path):
    rows = []
    with open(path, newline='') as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            rows.append(r)
    return rows


def aggregate(rows):
    # Count wins per ai level (winner owned by X or O)
    wins = defaultdict(int)
    games_per_level = defaultdict(int)
    ties = 0

    for r in rows:
        aX = int(r['ai_X_level'])
        aO = int(r['ai_O_level'])
        winner = r['winner']

        # Both AIs participated in this game
        games_per_level[aX] += 1
        games_per_level[aO] += 1

        if winner == 'Tie':
            ties += 1
        elif winner == 'X':
            wins[aX] += 1
        elif winner == 'O':
            wins[aO] += 1

    levels = sorted(set(list(games_per_level.keys()) + list(wins.keys())))
    stats = []
    for lv in levels:
        total = games_per_level.get(lv, 0)
        w = wins.get(lv, 0)
        rate = (w / total * 100) if total > 0 else 0.0
        stats.append((lv, total, w, rate))

    return stats, ties


def plot(stats, ties, out='tourney_plot.png'):
    levels = [s[0] for s in stats]
    rates = [s[3] for s in stats]

    plt.figure(figsize=(8, 5))
    bars = plt.bar([str(l) for l in levels], rates, color=['#2b8cbe', '#7bccc4', '#edf8b1'])
    plt.ylim(0, 100)
    plt.xlabel('AI Level')
    plt.ylabel('Win rate (%)')
    plt.title('AI Win Rate by Level (ties ignored)')

    for bar, s in zip(bars, stats):
        h = s[3]
        plt.text(bar.get_x() + bar.get_width()/2, h + 1, f"{h:.1f}%", ha='center')

    plt.tight_layout()
    plt.savefig(out)
    print(f'Plot saved to {out}')


def main():
    if len(sys.argv) < 2:
        print('Usage: python plot_stats.py results.csv')
        sys.exit(1)
    path = sys.argv[1]
    rows = load_results(path)
    stats, ties = aggregate(rows)
    print('Aggregated stats:')
    for lv, total, w, rate in stats:
        print(f'Level {lv}: games_seen={total}, wins={w}, win_rate={rate:.2f}%')
    print(f'Ties: {ties}')
    plot(stats, ties)

    # --- Enhanced plots ---
    # 1. Stacked bar plot for win/loss/tie rates by matchup
    from collections import defaultdict
    import matplotlib.pyplot as plt
    import pandas as pd
    # Build a DataFrame for easier grouping
    df = pd.DataFrame(rows)
    df['ai_X_level'] = df['ai_X_level'].astype(int)
    df['ai_O_level'] = df['ai_O_level'].astype(int)
    df['moves'] = df['moves'].astype(int)
    # Group by matchup and winner
    matchups = df.groupby(['ai_X_level', 'ai_O_level', 'winner']).size().unstack(fill_value=0)
    matchups = matchups.reset_index()
    # Ensure all columns present
    for col in ['X', 'O', 'Tie']:
        if col not in matchups.columns:
            matchups[col] = 0
    matchups['total'] = matchups[['X', 'O', 'Tie']].sum(axis=1)
    matchups['X_win_rate'] = matchups['X'] / matchups['total']
    matchups['O_win_rate'] = matchups['O'] / matchups['total']
    matchups['Tie_rate'] = matchups['Tie'] / matchups['total']
    labels = [f"L{int(x)} vs L{int(o)}" for x, o in zip(matchups['ai_X_level'], matchups['ai_O_level'])]
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(labels, matchups['X_win_rate'], label='X Wins', color='tab:blue')
    ax.bar(labels, matchups['Tie_rate'], bottom=matchups['X_win_rate'], label='Ties', color='tab:gray')
    ax.bar(labels, matchups['O_win_rate'], bottom=matchups['X_win_rate']+matchups['Tie_rate'], label='O Wins', color='tab:orange')
    ax.set_ylabel("Proportion")
    ax.set_title("Win/Draw/Loss Rates by AI Level Matchup")
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("stacked_bars.png")
    print("Saved stacked bar plot to stacked_bars.png")
    plt.close()

    # 2. Boxplot of game length by matchup
    df['matchup'] = df['ai_X_level'].astype(str) + " vs " + df['ai_O_level'].astype(str)
    plt.figure(figsize=(10, 6))
    df.boxplot(column='moves', by='matchup')
    plt.title("Game Length Distribution by Matchup")
    plt.suptitle("")
    plt.xlabel("Matchup")
    plt.ylabel("Moves per Game")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("game_length_box.png")
    print("Saved game length boxplot to game_length_box.png")
    plt.close()


if __name__ == '__main__':
    main()
