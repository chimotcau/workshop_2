import pygame
import sys
from engine_core import Board, WHITE, BLACK
from bot import SmartBot
from utils import opponent
from config import CELL_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
from config import WHITE_COLOR, BLACK_COLOR, HIGHLIGHT_COLOR
from config import STACK_WHITE, STACK_BLACK, MENU_BG, BUTTON_COLOR
from config import FONT_SIZE, BUTTON_FONT_SIZE, BOT_DELAY_MS

pygame.init()
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dipole")
FONT = pygame.font.SysFont(None, FONT_SIZE)
BUTTON_FONT = pygame.font.SysFont(None, BUTTON_FONT_SIZE)

def draw_board(board, selected=None, legal_moves=[]):
    for row in range(8):
        for col in range(8):
            color = WHITE_COLOR if (row + col) % 2 == 0 else BLACK_COLOR
            rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE,
                             CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(SCREEN, color, rect)
            if selected == (row, col):
                pygame.draw.rect(SCREEN, (0, 0, 255), rect, 4)
            if (row, col) in [move.end for move in legal_moves]:
                pygame.draw.rect(SCREEN, HIGHLIGHT_COLOR, rect, 4)
            piece = board.piece_at(row, col)
            if piece:
                stack_color = STACK_WHITE if piece.color == WHITE else STACK_BLACK
                pygame.draw.circle(SCREEN, stack_color,
                                 rect.center, CELL_SIZE // 2 - 5)
                text_color = (0, 0, 0) if piece.color == WHITE else (255, 255, 255)
                text = BUTTON_FONT.render(str(piece.size), True, text_color)
                SCREEN.blit(text, text.get_rect(center=rect.center))

def pos_to_coord(pos):
    x, y = pos
    return y // CELL_SIZE, x // CELL_SIZE

class Button:
    def __init__(self, text, rect, color=BUTTON_COLOR):
        self.text = text
        self.rect = pygame.Rect(rect)
        self.color = color

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=8)
        text_surf = BUTTON_FONT.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

def menu():
    buttons = [
        Button("Play PvP", (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 60, 200, 50)),
        Button("Play PvB", (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 50)),
        Button("Quit", (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 60, 200, 50))
    ]
    while True:
        SCREEN.fill(MENU_BG)
        title_surf = FONT.render("DIPOLE", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 120))
        SCREEN.blit(title_surf, title_rect)

        for btn in buttons:
            btn.draw(SCREEN)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for btn in buttons:
                    if btn.is_clicked(event.pos):
                        return btn.text

def game_loop(turn_player, bot_player=None):
    board = Board()
    running = True
    selected = None
    legal_moves = []
    last_bot_time = 0

    while running:
        SCREEN.fill((0, 0, 0))
        draw_board(board, selected, legal_moves)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if turn_player == WHITE or (turn_player == BLACK and bot_player is None):
                if event.type == pygame.MOUSEBUTTONDOWN:
                    row, col = pos_to_coord(event.pos)
                    piece = board.piece_at(row, col)
                    if piece and piece.color == turn_player:
                        selected = (row, col)
                        legal_moves = [move for move in board.get_all_legal_moves(turn_player)
                                     if move.start == (row, col)]
                    elif selected and (row, col) in [move.end for move in legal_moves]:
                        for move in legal_moves:
                            if move.end == (row, col):
                                board.move_piece(move)
                                break
                        selected = None
                        legal_moves = []
                        turn_player = opponent(turn_player)

        if bot_player and turn_player == bot_player.color:
            current_time = pygame.time.get_ticks()
            if current_time - last_bot_time > BOT_DELAY_MS:
                moves = board.get_all_legal_moves(bot_player.color)
                if moves:
                    move = bot_player.choose_move(board)
                    if move:
                        board.move_piece(move)
                turn_player = opponent(turn_player)
                last_bot_time = current_time

        if board.is_terminal():
            winner = board.winner()
            print(f"Game Over! Winner: {winner}")
            running = False
            pygame.time.wait(1000)

def main():
    while True:
        choice = menu()
        if choice == "Quit":
            pygame.quit()
            sys.exit()
        elif choice == "Play PvP":
            game_loop(turn_player=WHITE)
        elif choice == "Play PvB":
            bot = SmartBot(BLACK)
            game_loop(turn_player=WHITE, bot_player=bot)

if __name__ == "__main__":
    main()
