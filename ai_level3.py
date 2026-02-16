from tictactoe_engine import (
    available_moves,
    apply_move,
    check_winner,
    is_tie,
    get_next_player,
    X,
    O,
)


def get_move(board, player):

    moves = available_moves(board)
    if not moves:
        return None
    
    # If there's only one move, return it immediately
    if len(moves) == 1:
        return moves[0]
    
    best_move = None
    best_score = float('-inf')
    alpha = float('-inf')
    beta = float('inf')
    
    # Try each possible move and pick the one with the best score
    for move in moves:
        new_board = apply_move(board, move, player)
        score = minimax(new_board, get_next_player(player), player, alpha, beta, False)
        
        if score > best_score:
            best_score = score
            best_move = move
        
        alpha = max(alpha, score)
    
    return best_move


def minimax(board, current_player, maximizing_player, alpha, beta, is_maximizing):
 
    # Check terminal conditions
    winner = check_winner(board)
    if winner is not None:
        # Winner is the maximizing player: return positive score
        # Winner is the opponent: return negative score
        return 1 if winner == maximizing_player else -1
    
    if is_tie(board):
        return 0
    
    moves = available_moves(board)
    
    if is_maximizing:
        # Maximizing player's turn
        max_score = float('-inf')
        for move in moves:
            new_board = apply_move(board, move, current_player)
            score = minimax(
                new_board,
                get_next_player(current_player),
                maximizing_player,
                alpha,
                beta,
                False
            )
            max_score = max(max_score, score)
            alpha = max(alpha, score)
            
            # Beta cutoff: prune this branch
            if beta <= alpha:
                break
        
        return max_score
    else:
        # Minimizing player's turn
        min_score = float('inf')
        for move in moves:
            new_board = apply_move(board, move, current_player)
            score = minimax(
                new_board,
                get_next_player(current_player),
                maximizing_player,
                alpha,
                beta,
                True
            )
            min_score = min(min_score, score)
            beta = min(beta, score)
            
            # Alpha cutoff: prune this branch
            if beta <= alpha:
                break
        
        return min_score


def evaluate_move(board, move, player):

    new_board = apply_move(board, move, player)
    return minimax(
        new_board,
        get_next_player(player),
        player,
        float('-inf'),
        float('inf'),
        False
    )
