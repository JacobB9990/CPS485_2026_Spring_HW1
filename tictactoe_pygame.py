import pygame
import sys
from tictactoe_engine import (
    new_board,
    make_move_in_place,
    check_winner,
    is_tie,
    get_next_player,
    X,
    O,
)

# Import AI modules
import Level1.ai_player as ai1  # Level 1
import Level3.ai_level3 as ai3  # Level 3 
# import Level2.ai_level2 as ai2


WIDTH, HEIGHT = 600, 700
GRID_SIZE = 3
CELL_SIZE = WIDTH // GRID_SIZE
LINE_WIDTH = 8

BG_COLOR = (245, 245, 245)
LINE_COLOR = (40, 40, 40)
X_COLOR = (220, 60, 60)
O_COLOR = (60, 90, 220)
WIN_LINE_COLOR = (20, 160, 20)
TEXT_COLOR = (20, 20, 20)

FPS = 60


def get_move_from_player(mouse_pos):
    x, y = mouse_pos
    if x < 0 or x >= WIDTH or y < 0 or y >= WIDTH:
        return None
    col = x // CELL_SIZE
    row = y // CELL_SIZE
    return (row, col)


def get_winning_line(board):
    def center_of_cell(row, col):
        x = col * CELL_SIZE + CELL_SIZE // 2
        y = row * CELL_SIZE + CELL_SIZE // 2
        return (x, y)

    for r in range(GRID_SIZE):
        if board[r][0] is not None and all(
            board[r][c] == board[r][0] for c in range(GRID_SIZE)
        ):
            return (center_of_cell(r, 0), center_of_cell(r, GRID_SIZE - 1))
    for c in range(GRID_SIZE):
        if board[0][c] is not None and all(
            board[r][c] == board[0][c] for r in range(GRID_SIZE)
        ):
            return (center_of_cell(0, c), center_of_cell(GRID_SIZE - 1, c))
    if board[0][0] is not None and all(
        board[i][i] == board[0][0] for i in range(GRID_SIZE)
    ):
        return (center_of_cell(0, 0), center_of_cell(GRID_SIZE - 1, GRID_SIZE - 1))
    if board[0][GRID_SIZE - 1] is not None and all(
        board[i][GRID_SIZE - 1 - i] == board[0][GRID_SIZE - 1] for i in range(GRID_SIZE)
    ):
        return (center_of_cell(0, GRID_SIZE - 1), center_of_cell(GRID_SIZE - 1, 0))
    return None


def draw_grid(screen):
    for i in range(1, GRID_SIZE):
        pygame.draw.line(
            screen, LINE_COLOR, (i * CELL_SIZE, 0), (i * CELL_SIZE, WIDTH), LINE_WIDTH
        )
        pygame.draw.line(
            screen, LINE_COLOR, (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE), LINE_WIDTH
        )


def draw_marks(screen, board):
    padding = 40
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            mark = board[r][c]
            if mark is None:
                continue
            x0 = c * CELL_SIZE
            y0 = r * CELL_SIZE
            if mark == "X":
                pygame.draw.line(
                    screen,
                    X_COLOR,
                    (x0 + padding, y0 + padding),
                    (x0 + CELL_SIZE - padding, y0 + CELL_SIZE - padding),
                    10,
                )
                pygame.draw.line(
                    screen,
                    X_COLOR,
                    (x0 + CELL_SIZE - padding, y0 + padding),
                    (x0 + padding, y0 + CELL_SIZE - padding),
                    10,
                )
            elif mark == "O":
                center = (x0 + CELL_SIZE // 2, y0 + CELL_SIZE // 2)
                radius = CELL_SIZE // 2 - padding
                pygame.draw.circle(screen, O_COLOR, center, radius, 10)


def draw_win_line(screen, board):
    line = get_winning_line(board)
    if line:
        (x1, y1), (x2, y2) = line
        pygame.draw.line(screen, WIN_LINE_COLOR, (x1, y1), (x2, y2), 14)


def draw_status(
    screen, font, current_player, winner, tie, player_X_type, player_O_type, ai_level
):
    status_rect = pygame.Rect(0, WIDTH, WIDTH, HEIGHT - WIDTH)
    pygame.draw.rect(screen, BG_COLOR, status_rect)
    if winner:
        msg = f"{winner} wins! (R reset | X/O toggle | 1/2/3 AI)"
    elif tie:
        msg = f"Tie game! (R reset | X/O toggle | 1/2/3 AI)"
    else:
        msg = f"Turn: {current_player} | X: {player_X_type} | O: {player_O_type} | AI Level: {ai_level}"
    text = font.render(msg, True, TEXT_COLOR)
    screen.blit(text, (20, WIDTH + 40))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Tic Tac Toe")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 30)

    board = new_board()
    current_player = X
    winner = None
    tie = False

    # Player types
    player_X_type = "AI"  # or "Human"
    player_O_type = "AI"  # or "Human"
    ai_player_X = ai1
    ai_player_O = ai3
    ai_level = 1

    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    board = new_board()
                    current_player = X
                    winner = None
                    tie = False
                elif event.key == pygame.K_x:
                    player_X_type = "Human" if player_X_type == "AI" else "AI"
                    board = new_board()
                    current_player = X
                    winner = None
                    tie = False
                elif event.key == pygame.K_o:
                    player_O_type = "Human" if player_O_type == "AI" else "AI"
                    board = new_board()
                    current_player = X
                    winner = None
                    tie = False
                elif event.key == pygame.K_1:
                    ai_level = 1
                    ai_player_X = ai1
                    ai_player_O = ai1
                elif event.key == pygame.K_3:
                    ai_level = 3
                    ai_player_X = ai3
                    ai_player_O = ai3
                # Add keys for ai2/ai3 if needed

        # Determine current player type
        current_type = player_X_type if current_player == X else player_O_type

        # Human move
        if current_type == "Human" and not winner and not tie:
            if pygame.mouse.get_pressed()[0]:
                move = get_move_from_player(pygame.mouse.get_pos())
                if move and make_move_in_place(board, move, current_player):
                    winner = check_winner(board)
                    tie = is_tie(board)
                    if not winner and not tie:
                        current_player = get_next_player(current_player)

        # AI move
        if current_type == "AI" and not winner and not tie:
            ai_module = ai_player_X if current_player == X else ai_player_O
            move = ai_module.get_move(board, current_player)
            if move and make_move_in_place(board, move, current_player):
                winner = check_winner(board)
                tie = is_tie(board)
                if not winner and not tie:
                    current_player = get_next_player(current_player)

        screen.fill(BG_COLOR)
        draw_grid(screen)
        draw_marks(screen, board)
        if winner:
            draw_win_line(screen, board)
        draw_status(
            screen,
            font,
            current_player,
            winner,
            tie,
            player_X_type,
            player_O_type,
            ai_level,
        )
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()