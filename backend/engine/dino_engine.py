"""
Cyber-Dino Engine (Chrome Dinosaur Runner Mode for Multi-Model AI Arena).
Simulates continuous horizontal runner mechanics with increasing speed,
procedural obstacle generation (cacti, low/mid/high pterodactyls),
jumping/ducking kinematics, and hitbox collision detection.
"""

import math
import random
from typing import Dict, Any, List, Optional, Tuple


class DinoObstacle:
    def __init__(
        self,
        obstacle_id: int,
        obstacle_type: str,
        x: float,
        width: float,
        height: float,
        y: float = 0.0,
    ):
        self.id = obstacle_id
        self.type = obstacle_type  # cactus_small, cactus_double, cactus_large, ptero_low, ptero_mid, ptero_high
        self.x = x
        self.width = width
        self.height = height
        self.y = y  # 0.0 = on ground, >0 = flying altitude
        self.cleared = False

    def get_hitbox(self) -> Tuple[float, float, float, float]:
        # returns (min_x, max_x, min_y, max_y)
        # 2-pixel forgiving margin
        return (
            self.x + 2,
            self.x + self.width - 2,
            self.y,
            self.y + self.height - 2,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "x": round(self.x, 1),
            "y": round(self.y, 1),
            "width": self.width,
            "height": self.height,
            "cleared": self.cleared,
        }


class DinoGame:
    DINO_X = 50.0  # Dino fixed horizontal screen position
    STAND_WIDTH = 40.0
    STAND_HEIGHT = 44.0
    DUCK_WIDTH = 55.0
    DUCK_HEIGHT = 26.0

    GRAVITY = 0.65
    JUMP_VELOCITY = 11.5
    FAST_DROP_ACCEL = 1.2
    INITIAL_SPEED = 6.0
    MAX_SPEED = 14.0
    ACCELERATION = 0.0035

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = random.Random(seed)
        self.reset()

    def reset(self):
        self.rng = random.Random(self.seed)
        self.y = 0.0
        self.vy = 0.0
        self.is_jumping = False
        self.is_ducking = False
        self.state = "RUNNING"  # "RUNNING", "JUMPING", "DUCKING"
        self.speed = self.INITIAL_SPEED
        self.distance = 0.0
        self.obstacles_cleared = 0
        self.is_alive = True
        self.tick_count = 0
        self.obstacles: List[DinoObstacle] = []
        self._next_obstacle_id = 1
        self._min_spawn_gap = 280.0

        # Seed initial obstacles
        self._spawn_obstacle(x=250.0)
        self._spawn_obstacle(x=520.0)
        self._spawn_obstacle(x=800.0)

    def _spawn_obstacle(self, x: Optional[float] = None):
        if x is None:
            # Spawn offscreen to the right
            base_x = 680.0
            if self.obstacles:
                last_x = max(obs.x for obs in self.obstacles)
                base_x = max(base_x, last_x + self._min_spawn_gap + self.rng.uniform(30.0, 140.0))
            x = base_x

        # Obstacle types selection based on speed and difficulty
        choices = ["cactus_small", "cactus_double", "cactus_large"]
        if self.distance > 80:
            choices.extend(["ptero_low", "ptero_mid"])
        if self.distance > 180:
            choices.append("ptero_high")

        otype = self.rng.choice(choices)

        if otype == "cactus_small":
            w, h, y = 18.0, 36.0, 0.0
        elif otype == "cactus_double":
            w, h, y = 34.0, 38.0, 0.0
        elif otype == "cactus_large":
            w, h, y = 25.0, 48.0, 0.0
        elif otype == "ptero_low":
            w, h, y = 40.0, 28.0, 14.0  # Must jump
        elif otype == "ptero_mid":
            w, h, y = 40.0, 28.0, 42.0  # Must duck
        else:  # ptero_high
            w, h, y = 40.0, 28.0, 75.0  # Run or duck safely, don't jump into it

        obs = DinoObstacle(
            obstacle_id=self._next_obstacle_id,
            obstacle_type=otype,
            x=x,
            width=w,
            height=h,
            y=y,
        )
        self._next_obstacle_id += 1
        self.obstacles.append(obs)

    def get_dino_hitbox(self) -> Tuple[float, float, float, float]:
        # returns (min_x, max_x, min_y, max_y)
        w = self.DUCK_WIDTH if self.is_ducking else self.STAND_WIDTH
        h = self.DUCK_HEIGHT if self.is_ducking else self.STAND_HEIGHT
        # Forgiving hitbox margin for fair gameplay
        return (
            self.DINO_X + 4,
            self.DINO_X + w - 4,
            self.y,
            self.y + h - 2,
        )

    def check_collision(self, obs: DinoObstacle) -> bool:
        dx1, dx2, dy1, dy2 = self.get_dino_hitbox()
        ox1, ox2, oy1, oy2 = obs.get_hitbox()

        # AABB overlap test
        x_overlap = (dx1 < ox2) and (dx2 > ox1)
        y_overlap = (dy1 < oy2) and (dy2 > oy1)

        return x_overlap and y_overlap

    def step(self, action: str) -> Dict[str, Any]:
        """
        Execute one physics and game simulation step.
        action: "RUN", "JUMP", "DUCK"
        """
        if not self.is_alive:
            return self.get_state()

        self.tick_count += 1
        action = action.upper().strip()

        # Handle Action Input
        if action == "JUMP":
            if self.y == 0.0 and not self.is_jumping:
                self.vy = self.JUMP_VELOCITY
                self.is_jumping = True
                self.is_ducking = False
                self.state = "JUMPING"
        elif action == "DUCK":
            if self.y == 0.0:
                self.is_ducking = True
                self.state = "DUCKING"
            else:
                # Fast drop in mid-air
                self.vy -= self.FAST_DROP_ACCEL
                self.is_ducking = True
        else:  # "RUN" / default
            if self.y == 0.0:
                self.is_ducking = False
                self.is_jumping = False
                self.state = "RUNNING"

        # Apply Physics
        if self.is_jumping or self.y > 0.0:
            self.y += self.vy
            self.vy -= self.GRAVITY
            if self.y <= 0.0:
                self.y = 0.0
                self.vy = 0.0
                self.is_jumping = False
                self.state = "DUCKING" if self.is_ducking else "RUNNING"

        # Advance game progress
        self.distance += (self.speed / 6.0)
        self.speed = min(self.INITIAL_SPEED + self.ACCELERATION * self.tick_count, self.MAX_SPEED)

        # Move obstacles leftward
        for obs in self.obstacles:
            obs.x -= self.speed

            # Check if cleared
            if not obs.cleared and (obs.x + obs.width < self.DINO_X):
                obs.cleared = True
                self.obstacles_cleared += 1

            # Check collision
            if self.check_collision(obs):
                self.is_alive = False
                break

        # Remove offscreen obstacles (< -100px)
        self.obstacles = [obs for obs in self.obstacles if obs.x > -100.0]

        # Spawn new obstacles as needed
        if len(self.obstacles) < 4:
            self._spawn_obstacle()

        return self.get_state()

    def get_state(self) -> Dict[str, Any]:
        hitbox = self.get_dino_hitbox()
        return {
            "is_alive": self.is_alive,
            "tick": self.tick_count,
            "distance": round(self.distance, 1),
            "score": int(self.distance),
            "speed": round(self.speed, 2),
            "obstacles_cleared": self.obstacles_cleared,
            "dino": {
                "x": self.DINO_X,
                "y": round(self.y, 1),
                "vy": round(self.vy, 2),
                "state": self.state,
                "is_jumping": self.is_jumping,
                "is_ducking": self.is_ducking,
                "hitbox": {
                    "min_x": round(hitbox[0], 1),
                    "max_x": round(hitbox[1], 1),
                    "min_y": round(hitbox[2], 1),
                    "max_y": round(hitbox[3], 1),
                },
            },
            "obstacles": [obs.to_dict() for obs in self.obstacles],
        }
