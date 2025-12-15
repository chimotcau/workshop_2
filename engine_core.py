from copy import deepcopy

WHITE = 'white'
BLACK = 'black'
EMPTY = None

class Piece:
    def __init__(self, color, size=1):
        self.color = color
        self.size = size

    def __repr__(self):
        color_char = "W" if self.color == WHITE else "B"
        return f"{color_char}[{self.size}]"

class Move:
    def __init__(self, start, end, split=None, captures=None):
        self.start = start
        self.end = end
        self.split = split
        self.captures = captures or []

    def __repr__(self):
        return f"Move({self.start}->{self.end}, split={self.split})"

class Board:
    def __init__(self, size=8):
        self.size = size
        self.grid = [[EMPTY] * size for _ in range(size)]
        self.reset()

    def reset(self):
        board_size = self.size
        self.grid = [[EMPTY] * board_size for _ in range(board_size)]
        self.grid[0][3] = Piece(BLACK, 12)
        self.grid[7][4] = Piece(WHITE, 12)

    def in_bounds(self, row, col):
        return 0 <= row < self.size and 0 <= col < self.size

    def piece_at(self, row, col):
        return self.grid[row][col]

    def players_pieces(self, color):
        positions = []
        for row in range(self.size):
            for col in range(self.size):
                piece = self.grid[row][col]
                if piece and piece.color == color:
                    positions.append((row, col))
        return positions

    def get_all_legal_moves(self, color):
        moves = []
        for row, col in self.players_pieces(color):
            piece = self.grid[row][col]
            for split in range(1, piece.size + 1):
                moves.extend(self.get_piece_moves(row, col, piece, split))
        return moves

    def get_piece_moves(self, row, col, piece, split):
        moves = []
        size = split

        if piece.color == WHITE:
            forward_dirs = [(-1, 0), (-1, -1), (-1, 1)]
        else:
            forward_dirs = [(1, 0), (1, -1), (1, 1)]

        all_dirs = [(-1, 0), (1, 0), (0, -1), (0, 1),
                   (-1, -1), (-1, 1), (1, -1), (1, 1)]

        def valid_dark(check_row, check_col):
            return self.in_bounds(check_row, check_col) and ((check_row + check_col) % 2 == 1)

        for delta_row, delta_col in forward_dirs:
            target_row = row + delta_row * size
            target_col = col + delta_col * size
            if not self.in_bounds(target_row, target_col):
                continue
            if not valid_dark(target_row, target_col):
                continue
            destination = self.grid[target_row][target_col]
            if destination is None:
                moves.append(Move((row, col), (target_row, target_col), split))
            elif destination.color == piece.color:
                moves.append(Move((row, col), (target_row, target_col), split))
            elif destination.color != piece.color and destination.size <= split:
                moves.append(Move((row, col), (target_row, target_col), split,
                                captures=[(target_row, target_col)]))

        for delta_row, delta_col in all_dirs:
            target_row = row + delta_row * size
            target_col = col + delta_col * size
            if not self.in_bounds(target_row, target_col):
                continue
            destination = self.grid[target_row][target_col]
            if destination and destination.color != piece.color and destination.size <= split:
                moves.append(Move((row, col), (target_row, target_col), split,
                                captures=[(target_row, target_col)]))

        return moves

    def move_piece(self, move):
        start_row, start_col = move.start
        target_row, target_col = move.end
        piece = self.grid[start_row][start_col]
        if not piece:
            return

        moving_size = move.split
        piece.size -= moving_size
        if piece.size == 0:
            self.grid[start_row][start_col] = EMPTY
        moving_piece = Piece(piece.color, moving_size)

        for capture_row, capture_col in move.captures:
            if self.in_bounds(capture_row, capture_col):
                self.grid[capture_row][capture_col] = EMPTY

        destination = self.grid[target_row][target_col]
        if destination is None:
            self.grid[target_row][target_col] = moving_piece
        elif destination.color == piece.color:
            destination.size += moving_piece.size
        else:
            self.grid[target_row][target_col] = moving_piece

    def is_terminal(self):
        white_pieces = self.players_pieces(WHITE)
        black_pieces = self.players_pieces(BLACK)
        return not white_pieces or not black_pieces

    def winner(self):
        white_pieces = self.players_pieces(WHITE)
        black_pieces = self.players_pieces(BLACK)
        if white_pieces and not black_pieces:
            return WHITE
        if black_pieces and not white_pieces:
            return BLACK
        return None
