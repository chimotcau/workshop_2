import random
from engine_core import WHITE, BLACK
from config import CAPTURE_WEIGHT, SIZE_WEIGHT, FORWARD_WEIGHT

class SmartBot:
    def __init__(self, color):
        self.color = color

    def evaluate_move(self, board, move):
        score = 0
        from_row, from_col = move.start
        to_row, to_col = move.end
        piece = board.piece_at(from_row, from_col)

        score += CAPTURE_WEIGHT * len(move.captures)

        if piece:
            score += SIZE_WEIGHT * piece.size

        if piece:
            if self.color == WHITE:
                score += FORWARD_WEIGHT * (from_row - to_row)
            else:
                score += FORWARD_WEIGHT * (to_row - from_row)

        return score

    def choose_move(self, board):
        all_moves = board.get_all_legal_moves(self.color)

        if not all_moves:
            return None

        scored_moves = [(self.evaluate_move(board, move), move) for move in all_moves]
        max_score = max(score for score, _ in scored_moves)
        best_moves = [move for score, move in scored_moves if score == max_score]

        return random.choice(best_moves)
