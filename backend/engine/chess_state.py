"""
State representation and candidate generation for Chess AI Models.
Formats board into concise ASCII representation, FEN, material stats,
and scored candidate moves with human-readable criteria.
"""

import chess
from typing import Dict, Any, List
from backend.engine.chess_engine import ChessGame, evaluate_board, PIECE_VALUES


def build_chess_state(game: ChessGame) -> Dict[str, Any]:
    board = game.board
    legal_moves = list(board.legal_moves)
    is_white = (board.turn == chess.WHITE)

    # Score each legal move with 1-ply static evaluation
    scored_moves = []
    for m in legal_moves:
        is_capture = board.is_capture(m)
        is_check = board.gives_check(m)
        captured = board.piece_at(m.to_square)
        cap_val = PIECE_VALUES.get(captured.piece_type, 0) if captured else 0

        board.push(m)
        eval_score = evaluate_board(board)
        # Flip if it's black's turn so positive is always good for current player
        player_eval = eval_score if is_white else -eval_score
        board.pop()

        bonus = (cap_val * 2) + (50 if is_check else 0)
        total_heuristic = player_eval + bonus
        scored_moves.append((m, total_heuristic, is_capture, is_check, cap_val))

    # Sort descending by heuristic value
    scored_moves.sort(key=lambda x: x[1], reverse=True)

    # Select top 6 candidate moves for LLM/System-1 prompt
    top_moves = scored_moves[:6] if len(scored_moves) > 6 else scored_moves

    candidates: Dict[str, Dict[str, Any]] = {}
    criteria: Dict[str, str] = {}

    for idx, (m, score, is_cap, is_chk, cap_val) in enumerate(top_moves):
        uci_k = m.uci()
        san_str = board.san(m)
        desc_parts = [f"Play {san_str}"]

        if is_cap:
            desc_parts.append(f"captures piece (+{cap_val // 100} pts)")
        if is_chk:
            desc_parts.append("delivers CHECK")
        if not is_cap and not is_chk:
            desc_parts.append("improves piece activity and central control")

        desc_parts.append(f"eval: {score / 100.0:+.2f}")
        crit_text = "; ".join(desc_parts)

        candidates[uci_k] = {
            "uci": uci_k,
            "san": san_str,
            "from_square": chess.square_name(m.from_square),
            "to_square": chess.square_name(m.to_square),
            "score": score,
            "is_capture": is_cap,
            "is_check": is_chk,
        }
        criteria[uci_k] = crit_text

    # Board ASCII representation
    ascii_rows = []
    for rank in range(7, -1, -1):
        row_str = f"{rank + 1} | " + " ".join(
            (board.piece_at(chess.square(file, rank)).symbol() if board.piece_at(chess.square(file, rank)) else ".")
            for file in range(8)
        )
        ascii_rows.append(row_str)
    ascii_rows.append("   " + "-" * 15)
    ascii_rows.append("    a b c d e f g h")
    ascii_grid = "\n".join(ascii_rows)

    return {
        "fen": board.fen(),
        "turn": "white" if is_white else "black",
        "fullmove_number": board.fullmove_number,
        "is_check": board.is_check(),
        "legal_count": len(legal_moves),
        "candidates": candidates,
        "criteria": criteria,
        "ascii_grid": ascii_grid,
        "captured_by_white": game.captured_by_white,
        "captured_by_black": game.captured_by_black,
        "last_move": game.last_move,
    }
