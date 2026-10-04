"""
State representation builder for AI decision models (Jev, Laya, Ollama, Heuristics).
Provides structured JSON states, criteria descriptions, flood-fill vectors, and ASCII grids.
"""

from typing import Dict, Any, List, Tuple, Set
from collections import deque
from backend.engine.game import SnakeGame, DIR_VECTORS, OPPOSITE_DIR, Direction


def compute_flood_fill(
    game: SnakeGame,
    start_pos: Tuple[int, int],
    blocked_cells: Set[Tuple[int, int]],
) -> int:
    """Calculates number of reachable cells from start_pos using BFS."""
    if not game.is_valid_coordinate(*start_pos) or start_pos in blocked_cells:
        return 0

    visited = set()
    queue = deque([start_pos])
    visited.add(start_pos)

    while queue:
        x, y = queue.popleft()
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if (
                game.is_valid_coordinate(nx, ny)
                and (nx, ny) not in blocked_cells
                and (nx, ny) not in visited
            ):
                visited.add((nx, ny))
                queue.append((nx, ny))

    return len(visited)


def generate_ascii_grid(game: SnakeGame) -> str:
    """Renders visual ASCII grid representation for LLMs."""
    grid = [["." for _ in range(game.width)] for _ in range(game.height)]

    # Draw obstacles
    for ox, oy in game.obstacles:
        if game.is_valid_coordinate(ox, oy):
            grid[oy][ox] = "#"

    # Draw snake body
    for i, (bx, by) in enumerate(game.body):
        if game.is_valid_coordinate(bx, by):
            grid[by][bx] = "H" if i == 0 else "B"

    # Draw food
    fx, fy = game.food
    if game.is_valid_coordinate(fx, fy):
        grid[fy][fx] = "*"

    lines = ["+" + "---+" * game.width]
    for row in grid:
        lines.append("| " + " | ".join(row) + " |")
        lines.append("+" + "---+" * game.width)
    return "\n".join(lines)


def build_model_state(game: SnakeGame) -> Dict[str, Any]:
    """Generates rich comprehensive state representation for all model adapters."""
    hx, hy = game.head
    fx, fy = game.food
    dx = fx - hx
    dy = fy - hy

    # Relative food directions
    compass_x = "EAST" if dx > 0 else ("WEST" if dx < 0 else "")
    compass_y = "SOUTH" if dy > 0 else ("NORTH" if dy < 0 else "")
    compass = f"{compass_y}-{compass_x}".strip("-") if (compass_x or compass_y) else "ON_TARGET"

    blocked = set(game.body[:-1]) | game.obstacles
    manhattan_current = abs(dx) + abs(dy)

    move_evals: Dict[Direction, Dict[str, Any]] = {}
    criteria: Dict[str, str] = {}
    safe_moves: List[str] = []

    for d in ["UP", "DOWN", "LEFT", "RIGHT"]:
        eval_res = game.evaluate_move(d)
        is_safe = eval_res["safe"]
        tx, ty = eval_res["target"]

        if is_safe:
            safe_moves.append(d)
            dist_after = abs(fx - tx) + abs(fy - ty)
            approaches = dist_after < manhattan_current
            reaches_food = (tx, ty) == (fx, fy)
            space = compute_flood_fill(game, (tx, ty), blocked)

            if reaches_food:
                crit = f"BEST MOVE: Eats food directly at ({tx},{ty}). Available open space: {space} cells."
            elif approaches:
                crit = f"SAFE: Approaches food (distance decreases to {dist_after}). Available space: {space} cells."
            else:
                crit = f"SAFE: Moves away from food (distance increases to {dist_after}). Available space: {space} cells."
        else:
            reason = eval_res["reason"]
            if reason == "wall_collision":
                crit = f"FATAL DANGER: Crashes into outer wall boundary at ({tx},{ty})."
            elif reason == "obstacle_collision":
                crit = f"FATAL DANGER: Crashes into obstacle block at ({tx},{ty})."
            elif reason == "self_collision":
                crit = f"FATAL DANGER: Collides with snake's own body at ({tx},{ty})."
            elif reason == "reverse_into_neck":
                crit = f"ILLEGAL MOVE: 180-degree instant reversal into own neck."
            else:
                crit = f"FATAL DANGER: Unsafe move ({reason})."

            space = 0
            dist_after = 999

        move_evals[d] = {
            "safe": is_safe,
            "reason": eval_res["reason"],
            "target": list(eval_res["target"]),
            "reaches_food": is_safe and (eval_res["target"] == (fx, fy)),
            "distance_after": dist_after if is_safe else None,
            "flood_space": space,
            "criteria": crit,
        }
        criteria[d] = crit

    ascii_grid = generate_ascii_grid(game)

    return {
        "grid_size": [game.width, game.height],
        "snake_head": [hx, hy],
        "snake_body": [list(b) for b in game.body],
        "snake_length": len(game.body),
        "current_direction": game.current_direction,
        "food": [fx, fy],
        "food_direction": compass,
        "food_vector": [dx, dy],
        "manhattan_distance": manhattan_current,
        "safe_moves": safe_moves,
        "move_evaluations": move_evals,
        "criteria": criteria,
        "ascii_grid": ascii_grid,
    }
