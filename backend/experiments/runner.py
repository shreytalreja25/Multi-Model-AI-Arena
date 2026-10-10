"""
Headless Batch Experiment Runner for Scientific Benchmarking and Numerical Paper Analysis.
Executes games at maximum CPU speed without UI/sleep delays, capturing high-precision
latencies, decision accuracy, survival rates, tokenomics, and full replay traces.
"""

import os
import time
import json
import csv
import asyncio
import numpy as np
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable

from backend.engine.game import SnakeGame
from backend.engine.maze import generate_obstacles
from backend.engine.state_repr import build_model_state
from backend.models import create_default_agents, BaseSnakeAgent

from backend.engine.tetris import TetrisGame
from backend.engine.tetris_state import build_tetris_state
from backend.models.tetris_agents import create_default_tetris_agents, BaseTetrisAgent

from backend.engine.chess_engine import ChessGame
from backend.engine.chess_state import build_chess_state
from backend.models.chess_agents import create_default_chess_agents, BaseChessAgent, MinimaxChessAgent
import chess

from backend.engine.dino_engine import DinoGame
from backend.engine.dino_state import build_dino_state
from backend.models.dino_agents import create_default_dino_agents, BaseDinoAgent

EXPERIMENTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "experiments")
os.makedirs(EXPERIMENTS_DIR, exist_ok=True)


class HeadlessExperimentRunner:
    def __init__(
        self,
        game_mode: str = "snake",
        seeds: Optional[List[int]] = None,
        max_turns: int = 100,
        model_ids: Optional[List[str]] = None,
        maze_type: str = "open",
        grid_size: int = 8,
        fast_mode: bool = True,
    ):
        self.game_mode = game_mode
        self.seeds = seeds or [42, 101, 202, 303, 404, 505, 606, 707, 808, 909]
        self.max_turns = max_turns
        self.maze_type = maze_type
        self.grid_size = grid_size
        self.fast_mode = fast_mode

        if self.game_mode == "snake":
            self.agents = create_default_agents()
        elif self.game_mode == "tetris":
            self.agents = create_default_tetris_agents()
        elif self.game_mode == "chess":
            self.agents = create_default_chess_agents()
            self.black_opponent = MinimaxChessAgent(name="Minimax Tactical (Black)", model_id="minimax_black_opponent")
        else:  # dino
            self.agents = create_default_dino_agents()

        if model_ids:
            self.active_models = [m for m in model_ids if m in self.agents]
        else:
            self.active_models = list(self.agents.keys())

    async def _step_snake(self, game: SnakeGame, agent: BaseSnakeAgent, turn: int, seed: int) -> Dict[str, Any]:
        state_repr = build_model_state(game)
        dec = await agent.decide_move(state_repr)
        new_state = game.step(dec.direction)
        return {
            "turn": turn,
            "seed": seed,
            "model_id": agent.model_id,
            "name": agent.name,
            "decision": dec.model_dump(),
            "game_state": new_state,
        }

    async def _step_tetris(self, game: TetrisGame, agent: BaseTetrisAgent, turn: int, seed: int) -> Dict[str, Any]:
        pre_grid = [r[:] for r in game.grid]
        falling_piece = game.current_piece
        state_repr = build_tetris_state(game)
        dec = await agent.decide_placement(state_repr)
        drop_y = getattr(dec, "drop_y", 18)
        new_state = game.place_piece(dec.rotation, dec.column)

        commands = [
            f"SPAWN {falling_piece}",
            f"ROTATE {dec.rotation * 90}°",
            f"SHIFT COL {dec.column}",
            f"DROP Y:{drop_y}",
        ]
        if dec.lines_cleared > 0:
            commands.append(f"CLEAR {dec.lines_cleared} LINES")

        return {
            "turn": turn,
            "seed": seed,
            "model_id": agent.model_id,
            "name": agent.name,
            "decision": {
                "direction": f"COL_{dec.column}_ROT_{dec.rotation}",
                "confidence": dec.confidence,
                "latency_ms": dec.latency_ms,
                "lines_cleared": dec.lines_cleared,
                "holes_after": dec.holes_after,
                "is_safe": game.is_alive,
                "reasoning": dec.reasoning,
                "cost_usd": dec.cost_usd,
                "piece": falling_piece,
                "rotation": dec.rotation,
                "column": dec.column,
                "drop_y": drop_y,
                "commands": commands,
            },
            "pre_grid": pre_grid,
            "game_state": new_state,
        }

    async def _step_chess(self, game: ChessGame, agent: BaseChessAgent, turn: int, seed: int) -> Dict[str, Any]:
        state_repr = build_chess_state(game)
        white_dec = await agent.decide_move(state_repr, game.board)
        game.apply_move(white_dec.uci)

        black_reply = None
        if game.is_alive and game.board.turn == chess.BLACK:
            b_state = build_chess_state(game)
            b_dec = await self.black_opponent.decide_move(b_state, game.board)
            game.apply_move(b_dec.uci)
            black_reply = b_dec.san

        new_state = game.get_state()
        return {
            "turn": turn,
            "seed": seed,
            "model_id": agent.model_id,
            "name": agent.name,
            "decision": {
                "direction": white_dec.san,
                "san": white_dec.san,
                "uci": white_dec.uci,
                "from_square": white_dec.from_square,
                "to_square": white_dec.to_square,
                "confidence": white_dec.confidence,
                "latency_ms": white_dec.latency_ms,
                "is_safe": game.is_alive,
                "reasoning": white_dec.reasoning,
                "cost_usd": white_dec.cost_usd,
                "eval_score": white_dec.eval_score,
                "black_reply": black_reply,
            },
            "game_state": new_state,
        }

    async def _step_dino(self, game: DinoGame, agent: BaseDinoAgent, turn: int, seed: int) -> Dict[str, Any]:
        state_repr = build_dino_state(game)
        dec = await agent.decide_action(state_repr)
        new_state = game.step(dec.action)
        return {
            "turn": turn,
            "seed": seed,
            "model_id": agent.model_id,
            "name": agent.name,
            "decision": {
                "direction": dec.action,
                "action": dec.action,
                "confidence": dec.confidence,
                "latency_ms": dec.latency_ms,
                "is_safe": game.is_alive,
                "reasoning": dec.reasoning,
                "cost_usd": dec.cost_usd,
                "threat_evaluated": dec.threat_evaluated,
            },
            "game_state": new_state,
        }

    async def run(
        self,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> Dict[str, Any]:
        start_time = time.time()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        all_events: List[Dict[str, Any]] = []
        per_model_episode_stats: Dict[str, List[Dict[str, Any]]] = {m: [] for m in self.active_models}

        total_episodes = len(self.seeds)
        completed_episodes = 0

        for seed_idx, seed in enumerate(self.seeds):
            # Setup games for this seed
            games: Dict[str, Any] = {}
            if self.game_mode == "snake":
                obstacles = generate_obstacles(self.grid_size, self.grid_size, self.maze_type, 0.10, seed)
                for m_id in self.active_models:
                    games[m_id] = SnakeGame(self.grid_size, self.grid_size, seed, obstacles)
            elif self.game_mode == "tetris":
                for m_id in self.active_models:
                    games[m_id] = TetrisGame(10, 20, seed)
            elif self.game_mode == "chess":
                for m_id in self.active_models:
                    games[m_id] = ChessGame(seed=seed)
            else:  # dino
                for m_id in self.active_models:
                    games[m_id] = DinoGame(seed=seed)

            # Reset telemetry for this episode
            for m_id in self.active_models:
                self.agents[m_id].reset_telemetry()

            turn = 0
            while turn < self.max_turns:
                alive = [m_id for m_id in self.active_models if games[m_id].is_alive]
                if not alive:
                    break
                turn += 1

                tasks = []
                for m_id in alive:
                    g = games[m_id]
                    a = self.agents[m_id]
                    if self.game_mode == "snake":
                        tasks.append(self._step_snake(g, a, turn, seed))
                    elif self.game_mode == "tetris":
                        tasks.append(self._step_tetris(g, a, turn, seed))
                    elif self.game_mode == "chess":
                        tasks.append(self._step_chess(g, a, turn, seed))
                    else:
                        tasks.append(self._step_dino(g, a, turn, seed))

                results = await asyncio.gather(*tasks, return_exceptions=True)
                for r in results:
                    if isinstance(r, dict):
                        all_events.append(r)

            # Record stats for each model in this episode
            for m_id in self.active_models:
                g = games[m_id]
                a = self.agents[m_id]
                st = g.get_state()
                tel = a.get_summary_stats()

                if self.game_mode == "snake":
                    primary = st.get("score", 0)
                    secondary = st.get("steps", 0)
                elif self.game_mode == "tetris":
                    primary = st.get("lines_cleared", 0)
                    secondary = st.get("pieces_placed", 0)
                elif self.game_mode == "chess":
                    primary = st.get("material_diff", 0.0)
                    secondary = st.get("total_moves", 0)
                else:  # dino
                    primary = st.get("score", int(st.get("distance", 0)))
                    secondary = st.get("obstacles_cleared", 0)

                lats = getattr(a, "latencies_ms", [])
                p50 = float(np.percentile(lats, 50)) if lats else 0.0
                p90 = float(np.percentile(lats, 90)) if lats else 0.0
                p99 = float(np.percentile(lats, 99)) if lats else 0.0
                avg_lat = float(np.mean(lats)) if lats else 0.0

                per_model_episode_stats[m_id].append({
                    "seed": seed,
                    "primary_score": primary,
                    "secondary_metric": secondary,
                    "survived": st.get("is_alive", False),
                    "total_cost_usd": tel.get("total_cost_usd", 0.0),
                    "avg_latency_ms": avg_lat,
                    "p50_latency_ms": p50,
                    "p90_latency_ms": p90,
                    "p99_latency_ms": p99,
                })

            completed_episodes += 1
            if progress_callback:
                progress_callback({
                    "completed_episodes": completed_episodes,
                    "total_episodes": total_episodes,
                    "current_seed": seed,
                    "progress_pct": round((completed_episodes / total_episodes) * 100, 1),
                })

        total_duration = time.time() - start_time

        # Compute aggregate paper statistics per model
        summary_table: List[Dict[str, Any]] = []
        for m_id in self.active_models:
            episodes = per_model_episode_stats[m_id]
            agent = self.agents[m_id]

            scores = [e["primary_score"] for e in episodes]
            secondaries = [e["secondary_metric"] for e in episodes]
            lats_p50 = [e["p50_latency_ms"] for e in episodes]
            lats_avg = [e["avg_latency_ms"] for e in episodes]
            costs = [e["total_cost_usd"] for e in episodes]
            survivals = [1 if e["survived"] else 0 for e in episodes]

            summary_table.append({
                "model_id": m_id,
                "name": agent.name,
                "model_type": agent.model_type,
                "color": agent.color,
                "episodes": len(episodes),
                "score_mean": round(float(np.mean(scores)), 2),
                "score_std": round(float(np.std(scores)), 2),
                "score_median": round(float(np.median(scores)), 2),
                "score_max": round(float(np.max(scores)), 2),
                "metric_mean": round(float(np.mean(secondaries)), 2),
                "survival_rate_pct": round(float(np.mean(survivals)) * 100, 1),
                "latency_p50_ms": round(float(np.mean(lats_p50)), 1),
                "latency_avg_ms": round(float(np.mean(lats_avg)), 1),
                "total_cost_usd": round(float(np.sum(costs)), 6),
                "cost_per_1k_steps": round((float(np.sum(costs)) / max(1, sum(secondaries))) * 1000, 4),
            })

        # Sort summary table by score_mean descending
        summary_table.sort(key=lambda x: x["score_mean"], reverse=True)

        # File paths
        run_id = f"run_{timestamp}_{self.game_mode}"
        json_path = os.path.join(EXPERIMENTS_DIR, f"{run_id}.json")
        summary_csv_path = os.path.join(EXPERIMENTS_DIR, f"{run_id}_summary.csv")
        steps_csv_path = os.path.join(EXPERIMENTS_DIR, f"{run_id}_steps.csv")

        # 1. Save Full JSON (Includes all events for instant sped-up simulation replay)
        run_data = {
            "run_id": run_id,
            "timestamp": timestamp,
            "game_mode": self.game_mode,
            "total_duration_sec": round(total_duration, 2),
            "episodes": len(self.seeds),
            "seeds": self.seeds,
            "max_turns": self.max_turns,
            "grid_size": self.grid_size,
            "maze_type": self.maze_type,
            "models": [self.agents[m].name for m in self.active_models],
            "summary": summary_table,
            "events": all_events,
        }
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(run_data, f, indent=2)

        # 2. Save Summary CSV for Research Paper
        with open(summary_csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "model_id", "name", "model_type", "episodes",
                "score_mean", "score_std", "score_median", "score_max",
                "metric_mean", "survival_rate_pct", "latency_p50_ms", "latency_avg_ms",
                "total_cost_usd", "cost_per_1k_steps"
            ], extrasaction="ignore")
            writer.writeheader()
            for row in summary_table:
                writer.writerow(row)

        # 3. Save Step-by-Step Telemetry CSV
        with open(steps_csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["turn", "seed", "model_id", "name", "decision", "latency_ms", "confidence", "cost_usd", "is_alive"])
            for ev in all_events:
                dec = ev.get("decision", {})
                st = ev.get("game_state", {})
                writer.writerow([
                    ev.get("turn"),
                    ev.get("seed"),
                    ev.get("model_id"),
                    ev.get("name"),
                    dec.get("direction", dec.get("san", "")),
                    dec.get("latency_ms", 0),
                    dec.get("confidence", 0),
                    dec.get("cost_usd", 0),
                    st.get("is_alive", True),
                ])

        return {
            "run_id": run_id,
            "game_mode": self.game_mode,
            "total_duration_sec": round(total_duration, 2),
            "total_events": len(all_events),
            "json_path": json_path,
            "summary_csv_path": summary_csv_path,
            "steps_csv_path": steps_csv_path,
            "summary": summary_table,
        }
