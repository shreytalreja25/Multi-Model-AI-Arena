"""
Algorithmic A* Pathfinder & Flood-Fill Safety Agent.
Acts as the scientific ground-truth baseline for benchmarking AI models.
"""

import time
import heapq
from typing import Dict, Any, List, Tuple, Set, Optional
from backend.models.base import BaseSnakeAgent, DecisionResult


class HeuristicSnakeAgent(BaseSnakeAgent):
    def __init__(
        self,
        name: str = "A* Heuristic Pathfinder",
        model_id: str = "astar_heuristic",
        color: str = "#ec4899",
    ):
        super().__init__(
            name=name,
            model_id=model_id,
            model_type="heuristic",
            color=color,
            cost_per_1m_input=0.0,
            cost_per_1m_output=0.0,
        )

    def _find_astar_path(
        self,
        start: Tuple[int, int],
        goal: Tuple[int, int],
        width: int,
        height: int,
        blocked: Set[Tuple[int, int]],
    ) -> Optional[List[Tuple[int, int]]]:
        """Classic A* graph search on 2D grid."""
        if start == goal:
            return []

        open_set = []
        heapq.heappush(open_set, (0 + abs(start[0] - goal[0]) + abs(start[1] - goal[1]), 0, start, [start]))
        visited = {start: 0}

        while open_set:
            _, cost, current, path = heapq.heappop(open_set)
            if current == goal:
                return path

            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                nx, ny = current[0] + dx, current[1] + dy
                neighbor = (nx, ny)

                if 0 <= nx < width and 0 <= ny < height and (neighbor not in blocked or neighbor == goal):
                    new_cost = cost + 1
                    if neighbor not in visited or new_cost < visited[neighbor]:
                        visited[neighbor] = new_cost
                        heuristic = abs(nx - goal[0]) + abs(ny - goal[1])
                        heapq.heappush(open_set, (new_cost + heuristic, new_cost, neighbor, path + [neighbor]))

        return None

    async def decide_move(self, state: Dict[str, Any]) -> DecisionResult:
        t0 = time.perf_counter()
        width, height = state["grid_size"]
        hx, hy = state["snake_head"]
        fx, fy = state["food"]
        safe_moves = state.get("safe_moves", [])
        candidates = ["UP", "DOWN", "LEFT", "RIGHT"]

        blocked = set(tuple(b) for b in state["snake_body"][:-1])
        # Add obstacles
        # Obstacles are in state or can be inferred
        if not safe_moves:
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            res = DecisionResult(
                direction="RIGHT",
                confidence=0.1,
                latency_ms=round(elapsed_ms, 2),
                reasoning="No safe moves possible",
                is_safe=False,
            )
            self.record_decision(res)
            return res

        # Run A* to food
        path = self._find_astar_path((hx, hy), (fx, fy), width, height, blocked)

        chosen_dir = safe_moves[0]
        reason = "Fallback safe move"

        if path and len(path) > 1:
            next_step = path[1]
            dx, dy = next_step[0] - hx, next_step[1] - hy
            target_dir = {
                (0, -1): "UP",
                (0, 1): "DOWN",
                (-1, 0): "LEFT",
                (1, 0): "RIGHT",
            }.get((dx, dy))

            if target_dir in safe_moves:
                # Flood fill safety check
                space = state["move_evaluations"][target_dir]["flood_space"]
                if space >= len(state["snake_body"]) // 2:
                    chosen_dir = target_dir
                    reason = f"A* optimal path step to food ({len(path)-1} moves away)"
                else:
                    # Pick safe move with maximum flood fill space
                    chosen_dir = max(safe_moves, key=lambda d: state["move_evaluations"][d]["flood_space"])
                    reason = f"A* path too cramped (space={space}); pivoting to max survival flood area"
        else:
            # No path to food, maximize survival space (chase tail / largest area)
            chosen_dir = max(safe_moves, key=lambda d: state["move_evaluations"][d]["flood_space"])
            reason = "No open path to food; choosing maximum open flood space"

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        probs = {d: 0.02 for d in candidates}
        probs[chosen_dir] = 0.94

        res = DecisionResult(
            direction=chosen_dir,
            confidence=0.95,
            latency_ms=round(max(0.5, elapsed_ms), 2),
            input_tokens=0,
            output_tokens=0,
            cost_usd=0.0,
            reasoning=reason,
            probabilities=probs,
            is_safe=True,
            raw_response="astar_pathfinder_decision",
        )
        self.record_decision(res)
        return res
