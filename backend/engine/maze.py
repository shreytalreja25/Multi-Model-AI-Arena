"""
Configurable maze and obstacle generator for Snake Arena.
"""

from typing import Set, Tuple
import random


def generate_obstacles(
    width: int,
    height: int,
    maze_type: str = "open",
    density: float = 0.10,
    seed: int = 42,
) -> Set[Tuple[int, int]]:
    obstacles: Set[Tuple[int, int]] = set()
    rng = random.Random(seed)

    # Safe zone around starting snake (center)
    cx, cy = width // 2, height // 2
    reserved = {
        (cx, cy),
        (cx - 1, cy),
        (cx - 2, cy),
        (cx + 1, cy),
        (cx, cy - 1),
        (cx, cy + 1),
    }

    if maze_type == "open":
        return obstacles

    elif maze_type == "cross":
        # A central cross with openings
        for x in range(2, width - 2):
            if x != cx:
                obstacles.add((x, cy))
        for y in range(2, height - 2):
            if y != cy:
                obstacles.add((cx, y))

    elif maze_type == "four_rooms":
        # Divide board into 4 quadrants with doorway gaps
        mid_x, mid_y = width // 2, height // 2
        for x in range(width):
            if x not in (mid_x // 2, mid_x + mid_x // 2):
                obstacles.add((x, mid_y))
        for y in range(height):
            if y not in (mid_y // 2, mid_y + mid_y // 2):
                obstacles.add((mid_x, y))

    elif maze_type == "corridors":
        # Alternating horizontal bars
        for y in range(2, height - 2, 2):
            if (y // 2) % 2 == 0:
                for x in range(0, width - 2):
                    obstacles.add((x, y))
            else:
                for x in range(2, width):
                    obstacles.add((x, y))

    elif maze_type == "random_obstacles":
        all_cells = [
            (x, y)
            for x in range(width)
            for y in range(height)
            if (x, y) not in reserved
        ]
        target_count = int(len(all_cells) * max(0.05, min(0.35, density)))
        chosen = rng.sample(all_cells, min(target_count, len(all_cells)))
        obstacles.update(chosen)

    # Clean out reserved cells
    obstacles.difference_update(reserved)
    return obstacles
