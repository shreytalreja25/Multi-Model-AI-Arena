"""
Deterministic, seedable 2D Snake game engine for benchmarking AI models.
"""

from typing import List, Tuple, Set, Optional, Dict, Any
import random

Direction = str  # "UP", "DOWN", "LEFT", "RIGHT"

DIR_VECTORS: Dict[Direction, Tuple[int, int]] = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0),
}

OPPOSITE_DIR: Dict[Direction, Direction] = {
    "UP": "DOWN",
    "DOWN": "UP",
    "LEFT": "RIGHT",
    "RIGHT": "LEFT",
}


class SnakeGame:
    def __init__(
        self,
        width: int = 8,
        height: int = 8,
        seed: int = 42,
        obstacles: Optional[Set[Tuple[int, int]]] = None,
        max_idle_multiplier: int = 3,
    ):
        self.width = width
        self.height = height
        self.seed = seed
        self.rng = random.Random(seed)
        self.obstacles: Set[Tuple[int, int]] = set(obstacles) if obstacles else set()
        self.max_idle_steps = max(50, width * height * max_idle_multiplier)

        self.reset()

    def reset(self):
        self.rng = random.Random(self.seed)
        # Place snake in center-left moving RIGHT
        cx, cy = self.width // 2, self.height // 2
        # Initial 3-segment snake
        self.body: List[Tuple[int, int]] = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.current_direction: Direction = "RIGHT"
        self.score: int = 0
        self.steps: int = 0
        self.steps_since_food: int = 0
        self.is_alive: bool = True
        self.death_reason: Optional[str] = None
        self.food: Tuple[int, int] = self._spawn_food()
        self.history: List[Dict[str, Any]] = []

    @property
    def head(self) -> Tuple[int, int]:
        return self.body[0]

    def _spawn_food(self) -> Tuple[int, int]:
        occupied = set(self.body) | self.obstacles
        empty_cells = [
            (x, y)
            for x in range(self.width)
            for y in range(self.height)
            if (x, y) not in occupied
        ]
        if not empty_cells:
            # Snake filled the entire board! Game won
            return (-1, -1)
        return self.rng.choice(empty_cells)

    def is_valid_coordinate(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def evaluate_move(self, direction: Direction) -> Dict[str, Any]:
        """Check the outcome of a hypothetical move without advancing game state."""
        if direction not in DIR_VECTORS:
            return {"safe": False, "reason": "invalid_direction", "target": self.head}

        dx, dy = DIR_VECTORS[direction]
        hx, hy = self.head
        nx, ny = hx + dx, hy + dy

        # 180 reverse check
        if direction == OPPOSITE_DIR.get(self.current_direction) and len(self.body) > 1:
            return {"safe": False, "reason": "reverse_into_neck", "target": (nx, ny)}

        # Wall check
        if not self.is_valid_coordinate(nx, ny):
            return {"safe": False, "reason": "wall_collision", "target": (nx, ny)}

        # Obstacle check
        if (nx, ny) in self.obstacles:
            return {"safe": False, "reason": "obstacle_collision", "target": (nx, ny)}

        # Self body check (excluding the tail if the snake doesn't grow this step)
        tail = self.body[-1]
        will_eat = (nx, ny) == self.food
        body_to_check = set(self.body) if will_eat else set(self.body[:-1])
        if (nx, ny) in body_to_check:
            return {"safe": False, "reason": "self_collision", "target": (nx, ny)}

        return {
            "safe": True,
            "reason": "open_path",
            "target": (nx, ny),
            "eats_food": will_eat,
        }

    def step(self, direction: Direction) -> Dict[str, Any]:
        """Advance game state by one step in the given direction."""
        if not self.is_alive:
            return self.get_state()

        direction = direction.upper().strip()
        if direction not in DIR_VECTORS:
            direction = self.current_direction

        eval_res = self.evaluate_move(direction)
        self.steps += 1
        self.steps_since_food += 1

        if not eval_res["safe"]:
            self.is_alive = False
            self.death_reason = eval_res["reason"]
            self.history.append({
                "step": self.steps,
                "move": direction,
                "head": self.head,
                "food": self.food,
                "event": f"CRASH: {eval_res['reason']}",
                "score": self.score,
            })
            return self.get_state()

        # Advance snake
        nx, ny = eval_res["target"]
        self.current_direction = direction
        self.body.insert(0, (nx, ny))

        eats_food = (nx, ny) == self.food
        if eats_food:
            self.score += 1
            self.steps_since_food = 0
            self.food = self._spawn_food()
            if self.food == (-1, -1):
                self.is_alive = False
                self.death_reason = "victory_board_filled"
        else:
            self.body.pop()

        # Check starvation (infinite loop prevention)
        if self.steps_since_food >= self.max_idle_steps:
            self.is_alive = False
            self.death_reason = "starvation_timeout"

        step_record = {
            "step": self.steps,
            "move": direction,
            "head": self.head,
            "food": self.food,
            "event": "ATE_FOOD" if eats_food else "MOVE",
            "score": self.score,
            "eats_food": eats_food,
        }
        self.history.append(step_record)
        return self.get_state()

    def get_state(self) -> Dict[str, Any]:
        return {
            "width": self.width,
            "height": self.height,
            "head": list(self.head),
            "body": [list(segment) for segment in self.body],
            "food": list(self.food),
            "obstacles": [list(obs) for obs in self.obstacles],
            "direction": self.current_direction,
            "score": self.score,
            "steps": self.steps,
            "steps_since_food": self.steps_since_food,
            "is_alive": self.is_alive,
            "death_reason": self.death_reason,
        }
