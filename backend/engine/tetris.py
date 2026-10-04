"""
Deterministic, seedable 2D Tetris engine for multi-model AI benchmarking.
Implements standard 7-bag randomizer, 10x20 grid, wall kicks, line clears, and candidate placement analysis.
"""

from typing import List, Tuple, Dict, Any, Optional, Set
import random

# Standard Tetromino shapes (4 rotations each)
TETROMINOES: Dict[str, List[List[Tuple[int, int]]]] = {
    "I": [
        [(0, 1), (1, 1), (2, 1), (3, 1)],
        [(2, 0), (2, 1), (2, 2), (2, 3)],
        [(0, 2), (1, 2), (2, 2), (3, 2)],
        [(1, 0), (1, 1), (1, 2), (1, 3)],
    ],
    "O": [
        [(1, 0), (2, 0), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (2, 1)],
    ],
    "T": [
        [(1, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (1, 2)],
        [(1, 0), (0, 1), (1, 1), (1, 2)],
    ],
    "S": [
        [(1, 0), (2, 0), (0, 1), (1, 1)],
        [(1, 0), (1, 1), (2, 1), (2, 2)],
        [(1, 1), (2, 1), (0, 2), (1, 2)],
        [(0, 0), (0, 1), (1, 1), (1, 2)],
    ],
    "Z": [
        [(0, 0), (1, 0), (1, 1), (2, 1)],
        [(2, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (1, 2), (2, 2)],
        [(1, 0), (0, 1), (1, 1), (0, 2)],
    ],
    "J": [
        [(0, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (2, 2)],
        [(1, 0), (1, 1), (0, 2), (1, 2)],
    ],
    "L": [
        [(2, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (2, 2)],
        [(0, 1), (1, 1), (2, 1), (0, 2)],
        [(0, 0), (1, 0), (1, 1), (1, 2)],
    ],
}

PIECE_COLORS: Dict[str, str] = {
    "I": "#00f0ff",
    "O": "#facc15",
    "T": "#a855f7",
    "S": "#22c55e",
    "Z": "#ef4444",
    "J": "#3b82f6",
    "L": "#f97316",
}


class TetrisGame:
    def __init__(self, width: int = 10, height: int = 20, seed: int = 42):
        self.width = width
        self.height = height
        self.seed = seed
        self.rng = random.Random(seed)

        self.reset()

    def reset(self):
        self.rng = random.Random(self.seed)
        # Grid: 0 = empty, or string piece name e.g. "I", "T"
        self.grid: List[List[Optional[str]]] = [[None for _ in range(self.width)] for _ in range(self.height)]
        self.bag: List[str] = []

        self.score: int = 0
        self.lines_cleared: int = 0
        self.pieces_placed: int = 0
        self.is_alive: bool = True
        self.death_reason: Optional[str] = None

        self.current_piece: str = self._next_from_bag()
        self.next_piece: str = self._next_from_bag()

    def _next_from_bag(self) -> str:
        if not self.bag:
            self.bag = list(TETROMINOES.keys())
            self.rng.shuffle(self.bag)
        return self.bag.pop()

    def get_column_heights(self, grid: Optional[List[List[Optional[str]]]] = None) -> List[int]:
        g = grid if grid is not None else self.grid
        heights = []
        for x in range(self.width):
            h = 0
            for y in range(self.height):
                if g[y][x] is not None:
                    h = self.height - y
                    break
            heights.append(h)
        return heights

    def count_holes(self, grid: Optional[List[List[Optional[str]]]] = None) -> int:
        g = grid if grid is not None else self.grid
        holes = 0
        for x in range(self.width):
            covered = False
            for y in range(self.height):
                if g[y][x] is not None:
                    covered = True
                elif covered and g[y][x] is None:
                    holes += 1
        return holes

    def count_bumpiness(self, heights: List[int]) -> int:
        bumpiness = 0
        for i in range(len(heights) - 1):
            bumpiness += abs(heights[i] - heights[i + 1])
        return bumpiness

    def get_legal_placements(self) -> List[Dict[str, Any]]:
        """
        Calculates all valid (rotation, column) drop placements for current piece.
        Returns simulated outcomes (lines cleared, height, holes, bumpiness).
        """
        if not self.is_alive:
            return []

        rotations = TETROMINOES[self.current_piece]
        unique_rotations = []
        seen_coords = []
        for rot_idx, coords in enumerate(rotations):
            norm = tuple(sorted(coords))
            if norm not in seen_coords:
                seen_coords.append(norm)
                unique_rotations.append(rot_idx)

        placements = []

        for rot_idx in unique_rotations:
            coords = rotations[rot_idx]
            min_x = min(x for x, y in coords)
            max_x = max(x for x, y in coords)
            piece_w = max_x - min_x + 1

            for col in range(-min_x, self.width - max_x):
                drop_res = self._simulate_drop(coords, col)
                if drop_res["valid"]:
                    placements.append({
                        "rotation": rot_idx,
                        "column": col,
                        "drop_y": drop_res["drop_y"],
                        "lines_cleared": drop_res["lines_cleared"],
                        "holes_after": drop_res["holes"],
                        "max_height_after": drop_res["max_height"],
                        "bumpiness": drop_res["bumpiness"],
                        "landing_height": drop_res["landing_height"],
                        "creates_holes": drop_res["holes"] > self.count_holes(),
                    })

        return placements

    def _simulate_drop(self, coords: List[Tuple[int, int]], col_offset: int) -> Dict[str, Any]:
        """Simulates hard dropping piece at column offset."""
        # Find lowest valid drop row
        drop_y = 0
        while True:
            # Check if drop_y + 1 collides
            collides = False
            for px, py in coords:
                gx = px + col_offset
                gy = py + drop_y + 1
                if gy >= self.height or (0 <= gy < self.height and 0 <= gx < self.width and self.grid[gy][gx] is not None):
                    collides = True
                    break
            if collides:
                break
            drop_y += 1

        # Check if placement overflows above top
        is_above_ceiling = any(py + drop_y < 0 for px, py in coords)
        if is_above_ceiling or drop_y == 0 and any(self.grid[py + drop_y][px + col_offset] is not None for px, py in coords if 0 <= py + drop_y < self.height):
            return {"valid": False}

        # Clone grid and insert
        cloned = [row[:] for row in self.grid]
        for px, py in coords:
            gx = px + col_offset
            gy = py + drop_y
            if 0 <= gy < self.height and 0 <= gx < self.width:
                cloned[gy][gx] = self.current_piece

        # Count full lines
        lines_cleared = 0
        new_grid = []
        for row in cloned:
            if all(cell is not None for cell in row):
                lines_cleared += 1
            else:
                new_grid.append(row)
        while len(new_grid) < self.height:
            new_grid.insert(0, [None for _ in range(self.width)])

        heights = self.get_column_heights(new_grid)
        holes = self.count_holes(new_grid)
        bumpiness = self.count_bumpiness(heights)
        max_h = max(heights) if heights else 0
        landing_h = self.height - drop_y

        return {
            "valid": True,
            "drop_y": drop_y,
            "lines_cleared": lines_cleared,
            "holes": holes,
            "max_height": max_h,
            "bumpiness": bumpiness,
            "landing_height": landing_h,
        }

    def place_piece(self, rotation: int, column: int) -> Dict[str, Any]:
        """Locks piece at chosen rotation & column and clears lines."""
        if not self.is_alive:
            return self.get_state()

        rotations = TETROMINOES[self.current_piece]
        rot_idx = rotation % len(rotations)
        coords = rotations[rot_idx]

        drop_res = self._simulate_drop(coords, column)
        if not drop_res["valid"]:
            self.is_alive = False
            self.death_reason = "stack_overflow"
            return self.get_state()

        drop_y = drop_res["drop_y"]

        # Lock piece
        for px, py in coords:
            gx = px + column
            gy = py + drop_y
            if 0 <= gy < self.height and 0 <= gx < self.width:
                self.grid[gy][gx] = self.current_piece
            else:
                self.is_alive = False
                self.death_reason = "placed_out_of_bounds"

        # Line clear processing
        lines = 0
        cleared_grid = []
        for row in self.grid:
            if all(cell is not None for cell in row):
                lines += 1
            else:
                cleared_grid.append(row)

        while len(cleared_grid) < self.height:
            cleared_grid.insert(0, [None for _ in range(self.width)])
        self.grid = cleared_grid

        # Scoring: 100 for 1, 300 for 2, 500 for 3, 800 for 4 (Tetris!)
        line_scores = {0: 0, 1: 100, 2: 300, 3: 500, 4: 800}
        self.score += line_scores.get(lines, lines * 200)
        self.lines_cleared += lines
        self.pieces_placed += 1

        # Check if new piece can spawn
        self.current_piece = self.next_piece
        self.next_piece = self._next_from_bag()

        # Check if spawn is blocked (Game Over)
        spawn_coords = TETROMINOES[self.current_piece][0]
        spawn_col = self.width // 2 - 2
        for px, py in spawn_coords:
            gx = px + spawn_col
            gy = py
            if 0 <= gy < self.height and 0 <= gx < self.width and self.grid[gy][gx] is not None:
                self.is_alive = False
                self.death_reason = "stack_lockout"
                break

        return self.get_state()

    def get_state(self) -> Dict[str, Any]:
        return {
            "width": self.width,
            "height": self.height,
            "grid": self.grid,
            "current_piece": self.current_piece,
            "next_piece": self.next_piece,
            "score": self.score,
            "lines_cleared": self.lines_cleared,
            "pieces_placed": self.pieces_placed,
            "is_alive": self.is_alive,
            "death_reason": self.death_reason,
            "column_heights": self.get_column_heights(),
            "holes": self.count_holes(),
        }
