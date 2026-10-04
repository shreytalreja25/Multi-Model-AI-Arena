"""
State representation and placement scoring for Tetris AI models.
"""

from typing import Dict, Any, List, Tuple
from backend.engine.tetris import TetrisGame, PIECE_COLORS


def generate_tetris_ascii(game: TetrisGame) -> str:
    """Generates ASCII representation of current Tetris matrix."""
    lines = ["+" + "---+" * game.width]
    for row in game.grid:
        line_chars = []
        for cell in row:
            if cell is not None:
                line_chars.append(f"[{cell}]")
            else:
                line_chars.append(" . ")
        lines.append("|" + "".join(line_chars) + "|")
    lines.append("+" + "---+" * game.width)
    return "\n".join(lines)


def score_placement_dellacherie(p: Dict[str, Any]) -> float:
    """
    Pierre Dellacherie heuristic evaluation function for Tetris.
    Prioritizes low landing height, clearing lines, and strictly minimizing holes.
    """
    lh = p["landing_height"]
    lines = p["lines_cleared"]
    holes = p["holes_after"]
    bump = p["bumpiness"]

    # Classic Dellacherie weights
    weight_lh = -2.5
    weight_lines = 4.0
    weight_holes = -8.5
    weight_bump = -1.2

    score = (
        weight_lh * lh
        + weight_lines * (lines ** 2)
        + weight_holes * holes
        + weight_bump * bump
    )
    return score


def build_tetris_state(game: TetrisGame, top_k_candidates: int = 5) -> Dict[str, Any]:
    """Generates comprehensive state and top candidate placements for AI models."""
    legal_placements = game.get_legal_placements()
    if not legal_placements:
        return {
            "current_piece": game.current_piece,
            "next_piece": game.next_piece,
            "candidates": {},
            "criteria": {},
            "ascii_grid": generate_tetris_ascii(game),
            "legal_count": 0,
        }

    # Sort placements using Dellacherie heuristic to pick top-K interesting candidates + 1 trap
    scored = []
    for p in legal_placements:
        h_score = score_placement_dellacherie(p)
        scored.append((h_score, p))
    scored.sort(key=lambda x: x[0], reverse=True)

    # Take top candidate placements + maybe a risky/trap placement to test model discrimination
    selected = [item[1] for item in scored[:top_k_candidates]]

    candidates_map = {}
    criteria_map = {}

    for idx, p in enumerate(selected):
        c_id = f"POS_{idx}"
        col = p["column"]
        rot = p["rotation"]
        lines = p["lines_cleared"]
        holes = p["holes_after"]
        h_after = p["max_height_after"]

        if lines > 0:
            crit = f"EXCELLENT: Clears {lines} line(s)! Resulting height: {h_after}, total holes: {holes}."
        elif holes == game.count_holes():
            crit = f"SAFE & CLEAN: Drops cleanly at Column {col} (rot {rot}). Creates 0 new holes, height: {h_after}."
        else:
            crit = f"RISKY / SUBOPTIMAL: Drops at Column {col} (rot {rot}). Leaves {holes} holes buried under stack."

        p["key"] = c_id
        candidates_map[c_id] = p
        criteria_map[c_id] = crit

    return {
        "current_piece": game.current_piece,
        "next_piece": game.next_piece,
        "grid_size": [game.width, game.height],
        "score": game.score,
        "lines_cleared": game.lines_cleared,
        "pieces_placed": game.pieces_placed,
        "current_holes": game.count_holes(),
        "column_heights": game.get_column_heights(),
        "max_height": max(game.get_column_heights()) if game.get_column_heights() else 0,
        "candidates": candidates_map,
        "criteria": criteria_map,
        "ascii_grid": generate_tetris_ascii(game),
        "legal_count": len(legal_placements),
        "all_legal": legal_placements,
    }
