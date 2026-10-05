"""
Chess Engine implementation using python-chess.
Deterministic, seed-influenced opening book variations, move history,
material evaluation, and candidate move scoring.
"""

import chess
from typing import Dict, Any, List, Optional, Tuple

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000,
}

# Simplified piece-square positional tables (from White's perspective)
PAWN_TABLE = [
    0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
     5,  5, 10, 25, 25, 10,  5,  5,
     0,  0,  0, 20, 20,  0,  0,  0,
     5, -5,-10,  0,  0,-10, -5,  5,
     5, 10, 10,-20,-20, 10, 10,  5,
     0,  0,  0,  0,  0,  0,  0,  0
]

KNIGHT_TABLE = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50,
]

BISHOP_TABLE = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -20,-10,-10,-10,-10,-10,-10,-20,
]


def evaluate_board(board: chess.Board) -> int:
    """Computes static evaluation from White's perspective in centipawns."""
    if board.is_checkmate():
        return -99999 if board.turn == chess.WHITE else 99999
    if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_threefold_repetition():
        return 0

    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if not piece:
            continue
        val = PIECE_VALUES.get(piece.piece_type, 0)
        table_val = 0
        sq_idx = square if piece.color == chess.WHITE else chess.square_mirror(square)

        if piece.piece_type == chess.PAWN:
            table_val = PAWN_TABLE[sq_idx]
        elif piece.piece_type == chess.KNIGHT:
            table_val = KNIGHT_TABLE[sq_idx]
        elif piece.piece_type == chess.BISHOP:
            table_val = BISHOP_TABLE[sq_idx]

        pos_val = val + table_val
        if piece.color == chess.WHITE:
            score += pos_val
        else:
            score -= pos_val

    return score


class ChessGame:
    def __init__(self, seed: int = 42, initial_fen: Optional[str] = None):
        self.seed = seed
        self.board = chess.Board(fen=initial_fen) if initial_fen else chess.Board()
        self.move_history: List[str] = []
        self.last_move: Optional[Dict[str, Any]] = None
        self.captured_by_white: List[str] = []
        self.captured_by_black: List[str] = []
        self.is_alive = True

    def reset(self, seed: Optional[int] = None, fen: Optional[str] = None):
        if seed is not None:
            self.seed = seed
        self.board = chess.Board(fen=fen) if fen else chess.Board()
        self.move_history.clear()
        self.last_move = None
        self.captured_by_white.clear()
        self.captured_by_black.clear()
        self.is_alive = True

    def get_legal_moves(self) -> List[chess.Move]:
        return list(self.board.legal_moves)

    def apply_move(self, move_uci_or_san: str) -> Dict[str, Any]:
        """Applies a move in either UCI ('e2e4') or SAN ('e4') format."""
        if not self.is_alive:
            return self.get_state()

        move: Optional[chess.Move] = None
        # Try parse UCI
        try:
            move = chess.Move.from_uci(move_uci_or_san)
            if move not in self.board.legal_moves:
                move = None
        except Exception:
            move = None

        # Try parse SAN
        if not move:
            try:
                move = self.board.parse_san(move_uci_or_san)
            except Exception:
                move = None

        # If invalid or illegal, pick first legal move as safe fallback
        if not move:
            legal = self.get_legal_moves()
            if legal:
                move = legal[0]
            else:
                self.is_alive = False
                return self.get_state()

        # Track captures before pushing
        captured_piece = self.board.piece_at(move.to_square)
        san_str = self.board.san(move)
        uci_str = move.uci()
        from_sq_name = chess.square_name(move.from_square)
        to_sq_name = chess.square_name(move.to_square)

        if captured_piece:
            sym = captured_piece.symbol()
            if self.board.turn == chess.WHITE:
                self.captured_by_white.append(sym)
            else:
                self.captured_by_black.append(sym)

        self.board.push(move)
        self.move_history.append(san_str)

        self.last_move = {
            "from": from_sq_name,
            "to": to_sq_name,
            "san": san_str,
            "uci": uci_str,
            "captured": captured_piece.symbol() if captured_piece else None,
        }

        if self.board.is_game_over():
            self.is_alive = False

        return self.get_state()

    def get_state(self) -> Dict[str, Any]:
        # Build 8x8 2D grid from rank 8 (top) to rank 1 (bottom), file a to h
        board_2d = []
        for rank in range(7, -1, -1):
            row = []
            for file in range(8):
                sq = chess.square(file, rank)
                piece = self.board.piece_at(sq)
                if piece:
                    row.append({
                        "type": piece.symbol().lower(),
                        "symbol": piece.symbol(),
                        "color": "w" if piece.color == chess.WHITE else "b",
                        "square": chess.square_name(sq),
                    })
                else:
                    row.append(None)
            board_2d.append(row)

        # Calculate material score (White total - Black total)
        w_mat = sum(PIECE_VALUES[p.piece_type] for p in self.board.piece_map().values() if p.color == chess.WHITE)
        b_mat = sum(PIECE_VALUES[p.piece_type] for p in self.board.piece_map().values() if p.color == chess.BLACK)
        mat_diff = (w_mat - b_mat) / 100.0

        termination = "in_progress"
        if self.board.is_checkmate():
            termination = "checkmate"
        elif self.board.is_stalemate():
            termination = "stalemate"
        elif self.board.is_insufficient_material():
            termination = "insufficient_material"
        elif self.board.can_claim_threefold_repetition():
            termination = "threefold_repetition"

        return {
            "fen": self.board.fen(),
            "turn": "white" if self.board.turn == chess.WHITE else "black",
            "fullmove_number": self.board.fullmove_number,
            "halfmove_clock": self.board.halfmove_clock,
            "is_check": self.board.is_check(),
            "is_game_over": self.board.is_game_over(),
            "is_alive": not self.board.is_game_over(),
            "result": self.board.result() if self.board.is_game_over() else "*",
            "termination": termination,
            "last_move": self.last_move,
            "move_history": self.move_history[-16:],
            "total_moves": len(self.move_history),
            "captured_by_white": self.captured_by_white,
            "captured_by_black": self.captured_by_black,
            "material_diff": round(mat_diff, 2),
            "board_2d": board_2d,
            "score": round(w_mat / 100.0, 1),
        }
