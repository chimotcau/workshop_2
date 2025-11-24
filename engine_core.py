EMPTY = 0
WHITE = 1
BLACK = 2

ROWS = 8
COLS = 8

DIRS_FORWARD = {
    WHITE: [(-1, 0), (-1, -1), (-1, 1)],
    BLACK: [(1, 0), (1, -1), (1, 1)],
}

DIRS_ALL = [
    (-1, 0), (1, 0),
    (0, -1), (0, 1),
    (-1, -1), (-1, 1),
    (1, -1), (1, 1),
]

def inside(r, c):
    return 0 <= r < ROWS and 0 <= c < COLS

class Dipole:
    def __init__(self):
        self.grid = [[(EMPTY, 0) for _ in range(COLS)] for _ in range(ROWS)]
        self.turn = WHITE
        self.reset()

    def reset(self):
        self.grid[7][3] = (WHITE, 12)
        self.grid[0][4] = (BLACK, 12)

    def get_moves(self, side):
        moves = []
        for r in range(ROWS):
            for c in range(COLS):
                color, h = self.grid[r][c]
                if color != side or h == 0:
                    continue

                # Non-capturing moves: forward only
                for dr, dc in DIRS_FORWARD[side]:
                    nr = r + dr * h
                    nc = c + dc * h
                    if inside(nr, nc):
                        target_color, target_h = self.grid[nr][nc]
                        if target_color in (EMPTY, side):  # empty or merge
                            moves.append((r, c, h, nr, nc, []))

                # Capturing moves: all directions
                for dr, dc in DIRS_ALL:
                    nr = r + dr * h
                    nc = c + dc * h
                    if inside(nr, nc):
                        target_color, target_h = self.grid[nr][nc]
                        if target_color not in (EMPTY, side) and target_h <= h:
                            moves.append((r, c, h, nr, nc, [(nr, nc)]))
        return moves

    def apply(self, move):
        fr, fc, size, tr, tc, caps = move
        color, h = self.grid[fr][fc]
        self.grid[fr][fc] = (EMPTY, 0)

        if caps:
            # capture
            cr, cc = caps[0]
            self.grid[cr][cc] = (EMPTY, 0)
            self.grid[tr][tc] = (color, size)
        else:
            # merge or move
            target_color, target_h = self.grid[tr][tc]
            if target_color == color:
                self.grid[tr][tc] = (color, target_h + size)
            else:
                self.grid[tr][tc] = (color, size)

        # switch turn
        self.turn = BLACK if self.turn == WHITE else WHITE

    def winner(self):
        white = sum(h for row in self.grid for c, h in row if c == WHITE)
        black = sum(h for row in self.grid for c, h in row if c == BLACK)
        if white == 0: return BLACK
        if black == 0: return WHITE
        return None
