from copy import deepcopy

WHITE = 'white'
BLACK = 'black'
EMPTY = None

class Piece:
    def __init__(self, color, size=1):
        self.color = color
        self.size = size  

    def __repr__(self):
        c = "W" if self.color == WHITE else "B"
        return f"{c}[{self.size}]"

class Move:
    def __init__(self, fr, to, split=None, captures=None):
        self.fr = fr      
        self.to = to      
        self.split = split  
        self.captures = captures or []

    def __repr__(self):
        return f"Move({self.fr}->{self.to}, split={self.split}, caps={self.captures})"

class Board:
    def __init__(self, size=8):
        self.size = size
        self.grid = [[EMPTY]*size for _ in range(size)]
        self.reset()

    def reset(self):
        self.grid = [[EMPTY]*self.size for _ in range(self.size)]

        self.grid[0][3] = Piece(BLACK, 12)
        self.grid[7][4] = Piece(WHITE, 12)

    def in_bounds(self, r, c):
        return 0 <= r < self.size and 0 <= c < self.size

    def piece_at(self, r, c):
        return self.grid[r][c]

    def players_pieces(self, color):
        return [(r,c) for r in range(self.size) for c in range(self.size)
                if self.grid[r][c] and self.grid[r][c].color==color]

    def clone(self):
        return deepcopy(self)

    def get_all_legal_moves(self, color):
        moves = []
        for r,c in self.players_pieces(color):
            piece = self.grid[r][c]
            for split in range(1, piece.size+1):
                moves.extend(self._piece_moves(r,c,piece,split))
        return moves

    def _piece_moves(self, r, c, piece, split):
        moves = []
        size = split

        if piece.color == WHITE:
            forward_dirs = [(-1, 0), (-1, -1), (-1, 1)]
        else:
            forward_dirs = [(1, 0), (1, -1), (1, 1)]

        all_dirs = [(-1, 0), (1, 0), (0, -1), (0, 1),
                    (-1, -1), (-1, 1), (1, -1), (1, 1)]

        def valid_dark(rr, cc):
            return self.in_bounds(rr, cc) and ((rr + cc) % 2 == 1)

        for dr, dc in forward_dirs:
            tr = r + dr * size
            tc = c + dc * size
            if not self.in_bounds(tr, tc):
                continue  
            if not valid_dark(tr, tc):
                continue
            dest = self.grid[tr][tc]
            if dest is None:
                moves.append(Move((r, c), (tr, tc), split))
            elif dest.color == piece.color:
                moves.append(Move((r, c), (tr, tc), split))
            elif dest.color != piece.color and dest.size <= split:
                moves.append(Move((r, c), (tr, tc), split, captures=[(tr, tc)]))

        for dr, dc in all_dirs:
            tr = r + dr * size
            tc = c + dc * size
            if not self.in_bounds(tr, tc):
                continue
            dest = self.grid[tr][tc]
            if dest and dest.color != piece.color and dest.size <= split:
                moves.append(Move((r, c), (tr, tc), split, captures=[(tr, tc)]))

        return moves

    def move_piece(self, move):
        fr = move.fr
        tr, tc = move.to
        piece = self.grid[fr[0]][fr[1]]
        if not piece:
            return

        moving_size = move.split
        piece.size -= moving_size
        if piece.size == 0:
            self.grid[fr[0]][fr[1]] = EMPTY
        moving_piece = Piece(piece.color, moving_size)

        for cr, cc in move.captures:
            if self.in_bounds(cr, cc):
                self.grid[cr][cc] = EMPTY

        dest = self.grid[tr][tc]
        if dest is None:
            self.grid[tr][tc] = moving_piece
        elif dest.color == piece.color:
            dest.size += moving_piece.size
        else:
            self.grid[tr][tc] = moving_piece

    def is_terminal(self):
        return not self.players_pieces(WHITE) or not self.players_pieces(BLACK)

    def winner(self):
        if self.players_pieces(WHITE) and not self.players_pieces(BLACK):
            return WHITE
        if self.players_pieces(BLACK) and not self.players_pieces(WHITE):
            return BLACK
        return None