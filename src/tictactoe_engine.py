GRID_SIZE = 3

X = "X"
O = "O"
EMPTY = None


def new_board():
    return [[EMPTY for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]


def copy_board(board):
    return [row[:] for row in board]


def get_next_player(player):
    return O if player == X else X


def available_moves(board):
    moves = []
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if board[r][c] is EMPTY:
                moves.append((r, c))
    return moves


def is_legal_move(board, move):
    if move is None:
        return False

    r, c = move

    if r < 0 or r >= GRID_SIZE or c < 0 or c >= GRID_SIZE:
        return False

    return board[r][c] is EMPTY


def make_move_in_place(board, move, player):
    if not is_legal_move(board, move):
        return False
    r, c = move
    board[r][c] = player
    return True


def apply_move(board, move, player):
    new_b = copy_board(board)
    make_move_in_place(new_b, move, player)
    return new_b


def check_winner(board):
    for r in range(GRID_SIZE):
        if board[r][0] is not EMPTY and all(
            board[r][c] == board[r][0] for c in range(GRID_SIZE)
        ):
            return board[r][0]

    for c in range(GRID_SIZE):
        if board[0][c] is not EMPTY and all(
            board[r][c] == board[0][c] for r in range(GRID_SIZE)
        ):
            return board[0][c]

    if board[0][0] is not EMPTY and all(
        board[i][i] == board[0][0] for i in range(GRID_SIZE)
    ):
        return board[0][0]

    if board[0][GRID_SIZE - 1] is not EMPTY and all(
        board[i][GRID_SIZE - 1 - i] == board[0][GRID_SIZE - 1] for i in range(GRID_SIZE)
    ):
        return board[0][GRID_SIZE - 1]

    return None


def is_tie(board):
    return check_winner(board) is None and len(available_moves(board)) == 0


def is_terminal(board):
    return check_winner(board) is not None or is_tie(board)
