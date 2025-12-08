import pygame
from engine_core import Board, WHITE, BLACK, Piece, Move
from bot import SmartBot
import sys
import random

pygame.init()

CELL_SIZE = 60
BOARD_SIZE = 8
WIDTH = HEIGHT = CELL_SIZE * BOARD_SIZE
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dipole")
FONT = pygame.font.SysFont(None, 48)
BUTTON_FONT = pygame.font.SysFont(None, 36)

WHITE_COLOR = (245, 245, 220)
BLACK_COLOR = (50, 50, 50)
HIGHLIGHT_COLOR = (0, 255, 0)
STACK_COLOR = {WHITE: (255, 255, 255), BLACK: (0, 0, 0)}

def draw_board(board, selected=None, legal_moves=[]):
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            color = WHITE_COLOR if (r + c) % 2 == 0 else BLACK_COLOR
            rect = pygame.Rect(c*CELL_SIZE, r*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(SCREEN, color, rect)
            if selected == (r,c):
                pygame.draw.rect(SCREEN, (0,0,255), rect, 4)
            if (r,c) in [m.to for m in legal_moves]:
                pygame.draw.rect(SCREEN, HIGHLIGHT_COLOR, rect, 4)
            piece = board.piece_at(r,c)
            if piece:
                pygame.draw.circle(SCREEN, STACK_COLOR[piece.color],
                                   rect.center, CELL_SIZE//2 -5)
                text = BUTTON_FONT.render(str(piece.size), True,
                                   (0,0,0) if piece.color==WHITE else (255,255,255))
                SCREEN.blit(text, text.get_rect(center=rect.center))

def pos_to_coord(pos):
    x, y = pos
    return y // CELL_SIZE, x // CELL_SIZE

class Button:
    def __init__(self, text, rect, color=(100,100,100)):
        self.text = text
        self.rect = pygame.Rect(rect)
        self.color = color

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=8)
        text_surf = BUTTON_FONT.render(self.text, True, (255,255,255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

def menu():
    buttons = [
        Button("Play PvP", (WIDTH//2 - 100, HEIGHT//2 - 60, 200, 50)),
        Button("Play PvB", (WIDTH//2 - 100, HEIGHT//2, 200, 50)),
        Button("Quit", (WIDTH//2 - 100, HEIGHT//2 + 60, 200, 50))
    ]
    while True:
        SCREEN.fill((30,30,30))
        title_surf = FONT.render("DIPOLE", True, (255,255,255))
        title_rect = title_surf.get_rect(center=(WIDTH//2, HEIGHT//2 - 120))
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

    while running:
        SCREEN.fill((0,0,0))
        draw_board(board, selected, legal_moves)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if turn_player == WHITE or (turn_player == BLACK and bot_player is None):
                if event.type == pygame.MOUSEBUTTONDOWN:
                    r,c = pos_to_coord(event.pos)
                    piece = board.piece_at(r,c)
                    if piece and piece.color == turn_player:
                        selected = (r,c)
                        legal_moves = [m for m in board.get_all_legal_moves(turn_player)
                                       if m.fr == (r,c)]
                    elif selected and (r,c) in [m.to for m in legal_moves]:
                        move = [m for m in legal_moves if m.to==(r,c)][0]
                        board.move_piece(move)
                        selected = None
                        legal_moves = []
                        turn_player = BLACK if turn_player==WHITE else WHITE

        if bot_player and turn_player == bot_player.color:
            pygame.time.delay(300)
            moves = board.get_all_legal_moves(bot_player.color)
            if moves:
                move = random.choice(moves)
                board.move_piece(move)
            turn_player = WHITE if bot_player.color==BLACK else BLACK

        if board.is_terminal():
            winner = board.winner()
            print("Winner:", winner)
            running = False
            pygame.time.delay(1000)

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