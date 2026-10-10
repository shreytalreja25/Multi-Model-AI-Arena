"""
FastAPI Server & Real-time WebSocket Hub for Snake, Tetris & Chess Multi-Model AI Arena.
"""

import os
import asyncio
import json
import chess
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from backend.engine.game import SnakeGame
from backend.engine.maze import generate_obstacles
from backend.engine.state_repr import build_model_state
from backend.models import create_default_agents, discover_ollama_models, BaseSnakeAgent
from backend.models.ollama_agent import OllamaSnakeAgent
from backend.models.gemini_agent import GLOBAL_GEMINI_TRACKER

from backend.engine.tetris import TetrisGame
from backend.engine.tetris_state import build_tetris_state
from backend.models.tetris_agents import create_default_tetris_agents, BaseTetrisAgent

from backend.engine.chess_engine import ChessGame
from backend.engine.chess_state import build_chess_state
from backend.models.chess_agents import create_default_chess_agents, BaseChessAgent, MinimaxChessAgent

from backend.engine.dino_engine import DinoGame
from backend.engine.dino_state import build_dino_state
from backend.models.dino_agents import create_default_dino_agents, BaseDinoAgent

ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(ENV_PATH)

app = FastAPI(title="Multi-Model AI Arena (Snake, Tetris, Chess & Dino)", version="4.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ArenaCoordinator:
    def __init__(self):
        self.game_mode = "snake"  # "snake", "tetris", or "chess"
        self.width = 8
        self.height = 8
        self.seed = 42
        self.maze_type = "open"
        self.density = 0.10
        self.step_delay_ms = 300
        self.is_running = False
        self.turn = 0

        # Snake agents & games
        self.snake_agents: Dict[str, BaseSnakeAgent] = create_default_agents()
        self.active_snake_models: List[str] = list(self.snake_agents.keys())
        self.snake_games: Dict[str, SnakeGame] = {}

        # Tetris agents & games
        self.tetris_agents: Dict[str, BaseTetrisAgent] = create_default_tetris_agents()
        self.active_tetris_models: List[str] = list(self.tetris_agents.keys())
        self.tetris_games: Dict[str, TetrisGame] = {}

        # Chess agents & games (Each model plays White vs Minimax Benchmark playing Black)
        self.chess_agents: Dict[str, BaseChessAgent] = create_default_chess_agents()
        self.active_chess_models: List[str] = list(self.chess_agents.keys())
        self.chess_games: Dict[str, ChessGame] = {}
        self.black_opponent = MinimaxChessAgent(name="Minimax Tactical (Black)", model_id="minimax_black_opponent")

        # Cyber-Dino agents & games (Chrome Dinosaur Runner Mode)
        self.dino_agents: Dict[str, BaseDinoAgent] = create_default_dino_agents()
        self.active_dino_models: List[str] = list(self.dino_agents.keys())
        self.dino_games: Dict[str, DinoGame] = {}

        self.log_history: List[Dict[str, Any]] = []
        self.connections: List[WebSocket] = []
        self._loop_task: Optional[asyncio.Task] = None

        self.init_games()

    def init_games(self):
        self.turn = 0
        if self.game_mode == "snake":
            obstacles = generate_obstacles(
                width=self.width,
                height=self.height,
                maze_type=self.maze_type,
                density=self.density,
                seed=self.seed,
            )
            self.snake_games.clear()
            for m_id in self.active_snake_models:
                if m_id in self.snake_agents:
                    self.snake_agents[m_id].reset_telemetry()
                    self.snake_games[m_id] = SnakeGame(
                        width=self.width,
                        height=self.height,
                        seed=self.seed,
                        obstacles=obstacles,
                    )
        elif self.game_mode == "tetris":
            t_width = 10
            t_height = 20
            self.tetris_games.clear()
            for m_id in self.active_tetris_models:
                if m_id in self.tetris_agents:
                    self.tetris_agents[m_id].reset_telemetry()
                    self.tetris_games[m_id] = TetrisGame(
                        width=t_width,
                        height=t_height,
                        seed=self.seed,
                    )
        elif self.game_mode == "chess":
            # Chess setup
            self.chess_games.clear()
            for m_id in self.active_chess_models:
                if m_id in self.chess_agents:
                    self.chess_agents[m_id].reset_telemetry()
                    self.chess_games[m_id] = ChessGame(seed=self.seed)
        elif self.game_mode == "dino":
            # Cyber-Dino setup
            self.dino_games.clear()
            for m_id in self.active_dino_models:
                if m_id in self.dino_agents:
                    self.dino_agents[m_id].reset_telemetry()
                    self.dino_games[m_id] = DinoGame(seed=self.seed)

    async def connect_client(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)
        await self.broadcast_full_state([websocket])

    def disconnect_client(self, websocket: WebSocket):
        if websocket in self.connections:
            self.connections.remove(websocket)

    async def broadcast(self, payload: Dict[str, Any]):
        if not self.connections:
            return
        dead = []
        msg = json.dumps(payload)
        for ws in self.connections:
            try:
                await ws.send_text(msg)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect_client(ws)

    def get_full_state_payload(self) -> Dict[str, Any]:
        models_data = []

        if self.game_mode == "snake":
            for m_id in self.active_snake_models:
                game = self.snake_games.get(m_id)
                agent = self.snake_agents.get(m_id)
                if not game or not agent:
                    continue
                models_data.append({
                    "model_id": m_id,
                    "name": agent.name,
                    "model_type": agent.model_type,
                    "color": agent.color,
                    "game_state": game.get_state(),
                    "telemetry": agent.get_summary_stats(),
                })
        elif self.game_mode == "tetris":
            for m_id in self.active_tetris_models:
                game = self.tetris_games.get(m_id)
                agent = self.tetris_agents.get(m_id)
                if not game or not agent:
                    continue
                models_data.append({
                    "model_id": m_id,
                    "name": agent.name,
                    "model_type": agent.model_type,
                    "color": agent.color,
                    "game_state": game.get_state(),
                    "telemetry": agent.get_summary_stats(),
                })
        elif self.game_mode == "chess":
            for m_id in self.active_chess_models:
                game = self.chess_games.get(m_id)
                agent = self.chess_agents.get(m_id)
                if not game or not agent:
                    continue
                models_data.append({
                    "model_id": m_id,
                    "name": agent.name,
                    "model_type": agent.model_type,
                    "color": agent.color,
                    "game_state": game.get_state(),
                    "telemetry": agent.get_summary_stats(),
                })
        elif self.game_mode == "dino":
            for m_id in self.active_dino_models:
                game = self.dino_games.get(m_id)
                agent = self.dino_agents.get(m_id)
                if not game or not agent:
                    continue
                models_data.append({
                    "model_id": m_id,
                    "name": agent.name,
                    "model_type": agent.model_type,
                    "color": agent.color,
                    "game_state": game.get_state(),
                    "telemetry": agent.get_summary_stats(),
                })

        active_list = (
            self.active_snake_models if self.game_mode == "snake"
            else self.active_tetris_models if self.game_mode == "tetris"
            else self.active_chess_models if self.game_mode == "chess"
            else self.active_dino_models
        )

        return {
            "type": "FULL_STATE",
            "game_mode": self.game_mode,
            "turn": self.turn,
            "is_running": self.is_running,
            "safety_status": GLOBAL_GEMINI_TRACKER.get_status_summary(),
            "config": {
                "game_mode": self.game_mode,
                "width": self.width if self.game_mode == "snake" else 10 if self.game_mode == "tetris" else 8,
                "height": self.height if self.game_mode == "snake" else 20 if self.game_mode == "tetris" else 8,
                "seed": self.seed,
                "maze_type": self.maze_type,
                "step_delay_ms": self.step_delay_ms,
                "active_models": active_list,
            },
            "models": models_data,
        }

    async def broadcast_full_state(self, targets: Optional[List[WebSocket]] = None):
        payload = self.get_full_state_payload()
        msg = json.dumps(payload)
        target_list = targets or self.connections
        for ws in list(target_list):
            try:
                await ws.send_text(msg)
            except Exception:
                self.disconnect_client(ws)

    async def step_snake_model(self, m_id: str) -> Optional[Dict[str, Any]]:
        game = self.snake_games.get(m_id)
        agent = self.snake_agents.get(m_id)
        if not game or not agent or not game.is_alive:
            return None

        state_repr = build_model_state(game)
        decision = await agent.decide_move(state_repr)
        new_state = game.step(decision.direction)

        event = {
            "turn": self.turn,
            "game_mode": "snake",
            "model_id": m_id,
            "name": agent.name,
            "model_type": agent.model_type,
            "color": agent.color,
            "decision": decision.model_dump(),
            "game_state": new_state,
            "telemetry": agent.get_summary_stats(),
            "state_repr": {
                "head": state_repr["snake_head"],
                "food": state_repr["food"],
                "food_direction": state_repr["food_direction"],
                "criteria": state_repr["criteria"],
                "ascii_grid": state_repr["ascii_grid"],
            },
        }
        self.log_history.append(event)
        return event

    async def step_tetris_model(self, m_id: str) -> Optional[Dict[str, Any]]:
        game = self.tetris_games.get(m_id)
        agent = self.tetris_agents.get(m_id)
        if not game or not agent or not game.is_alive:
            return None

        pre_grid = [row[:] for row in game.grid]
        falling_piece = game.current_piece

        state_repr = build_tetris_state(game)
        decision = await agent.decide_placement(state_repr)
        drop_y = getattr(decision, "drop_y", 18)
        new_state = game.place_piece(decision.rotation, decision.column)

        commands = [
            f"SPAWN {falling_piece}",
            f"ROTATE {decision.rotation * 90}°",
            f"SHIFT COL {decision.column}",
            f"DROP Y:{drop_y}",
        ]
        if decision.lines_cleared > 0:
            commands.append(f"CLEAR {decision.lines_cleared} LINES")

        event = {
            "turn": self.turn,
            "game_mode": "tetris",
            "model_id": m_id,
            "name": agent.name,
            "model_type": agent.model_type,
            "color": agent.color,
            "decision": {
                "direction": f"COL_{decision.column}_ROT_{decision.rotation}",
                "confidence": decision.confidence,
                "latency_ms": decision.latency_ms,
                "lines_cleared": decision.lines_cleared,
                "holes_after": decision.holes_after,
                "is_safe": game.is_alive,
                "reasoning": decision.reasoning,
                "cost_usd": decision.cost_usd,
                "piece": falling_piece,
                "rotation": decision.rotation,
                "column": decision.column,
                "drop_y": drop_y,
                "commands": commands,
            },
            "pre_grid": pre_grid,
            "game_state": new_state,
            "telemetry": agent.get_summary_stats(),
            "state_repr": {
                "current_piece": state_repr["current_piece"],
                "next_piece": state_repr["next_piece"],
                "criteria": state_repr["criteria"],
                "ascii_grid": state_repr["ascii_grid"],
            },
        }
        self.log_history.append(event)
        return event

    async def step_chess_model(self, m_id: str) -> Optional[Dict[str, Any]]:
        game = self.chess_games.get(m_id)
        agent = self.chess_agents.get(m_id)
        if not game or not agent or not game.is_alive:
            return None

        # 1. AI Model plays as WHITE
        state_repr = build_chess_state(game)
        white_decision = await agent.decide_move(state_repr, game.board)
        game.apply_move(white_decision.uci)

        # 2. Benchmark Minimax Opponent immediately plays as BLACK if still alive
        black_move_san = None
        if game.is_alive and game.board.turn == chess.BLACK:
            black_state = build_chess_state(game)
            black_dec = await self.black_opponent.decide_move(black_state, game.board)
            game.apply_move(black_dec.uci)
            black_move_san = black_dec.san

        new_state = game.get_state()

        # Update win/loss records
        if not game.is_alive:
            res = new_state.get("result", "*")
            if res == "1-0":
                agent.wins += 1
            elif res == "0-1":
                agent.losses += 1
            else:
                agent.draws += 1

        commands = [
            f"WHITE {agent.name}: {white_decision.san} ({white_decision.from_square} -> {white_decision.to_square})",
        ]
        if black_move_san:
            commands.append(f"BLACK Minimax: {black_move_san}")
        if new_state.get("is_check"):
            commands.append("CHECK!")
        if not game.is_alive:
            commands.append(f"GAME OVER: {new_state.get('termination', 'finished').upper()}")

        event = {
            "turn": self.turn,
            "game_mode": "chess",
            "model_id": m_id,
            "name": agent.name,
            "model_type": agent.model_type,
            "color": agent.color,
            "decision": {
                "direction": white_decision.san,
                "san": white_decision.san,
                "uci": white_decision.uci,
                "from_square": white_decision.from_square,
                "to_square": white_decision.to_square,
                "confidence": white_decision.confidence,
                "latency_ms": white_decision.latency_ms,
                "is_safe": game.is_alive,
                "reasoning": white_decision.reasoning,
                "cost_usd": white_decision.cost_usd,
                "eval_score": white_decision.eval_score,
                "commands": commands,
                "black_reply": black_move_san,
            },
            "game_state": new_state,
            "telemetry": agent.get_summary_stats(),
            "state_repr": {
                "fen": new_state["fen"],
                "turn": new_state["turn"],
                "fullmove_number": new_state["fullmove_number"],
                "criteria": state_repr["criteria"],
                "ascii_grid": state_repr["ascii_grid"],
            },
        }
        self.log_history.append(event)
        return event

    async def step_dino_model(self, m_id: str) -> Optional[Dict[str, Any]]:
        game = self.dino_games.get(m_id)
        agent = self.dino_agents.get(m_id)
        if not game or not agent or not game.is_alive:
            return None

        state_repr = build_dino_state(game)
        decision = await agent.decide_action(state_repr)
        new_state = game.step(decision.action)

        if not game.is_alive and agent.max_distance < game.distance:
            agent.max_distance = game.distance
        agent.obstacles_cleared = game.obstacles_cleared

        imm = state_repr.get("immediate_obstacle")
        commands = [
            f"ACTION: {decision.action}",
            f"SPEED: {new_state['speed']} px/f",
            f"DIST: {int(new_state['distance'])}m",
        ]
        if imm:
            commands.append(f"HAZARD: {imm['type'].upper()} ({int(state_repr['immediate_distance_px'])}px)")

        event = {
            "turn": self.turn,
            "game_mode": "dino",
            "model_id": m_id,
            "name": agent.name,
            "model_type": agent.model_type,
            "color": agent.color,
            "decision": {
                "direction": decision.action,
                "action": decision.action,
                "confidence": decision.confidence,
                "latency_ms": decision.latency_ms,
                "is_safe": game.is_alive,
                "reasoning": decision.reasoning,
                "cost_usd": decision.cost_usd,
                "threat_evaluated": decision.threat_evaluated,
                "commands": commands,
            },
            "game_state": new_state,
            "telemetry": agent.get_summary_stats(),
            "state_repr": {
                "speed": state_repr["speed"],
                "distance": state_repr["distance"],
                "criteria": state_repr["criteria"],
                "ascii_grid": state_repr["ascii_grid"],
                "immediate_obstacle": state_repr["immediate_obstacle"],
                "immediate_distance_px": state_repr["immediate_distance_px"],
                "optimal_action": state_repr["optimal_action"],
            },
        }
        self.log_history.append(event)
        return event

    async def execute_turn(self):
        if self.game_mode == "snake":
            alive = [m for m in self.active_snake_models if self.snake_games.get(m) and self.snake_games[m].is_alive]
            if not alive:
                self.is_running = False
                await self.broadcast({"type": "GAME_OVER", "game_mode": "snake", "turn": self.turn})
                return
            self.turn += 1
            tasks = [self.step_snake_model(m) for m in alive]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            valid = [r for r in results if isinstance(r, dict) and r is not None]
            all_alive = any(self.snake_games[m].is_alive for m in self.active_snake_models if m in self.snake_games)
            await self.broadcast({
                "type": "TICK",
                "game_mode": "snake",
                "turn": self.turn,
                "events": valid,
                "is_running": self.is_running and all_alive,
                "safety_status": GLOBAL_GEMINI_TRACKER.get_status_summary(),
            })
            if not all_alive:
                self.is_running = False

        elif self.game_mode == "tetris":
            alive = [m for m in self.active_tetris_models if self.tetris_games.get(m) and self.tetris_games[m].is_alive]
            if not alive:
                self.is_running = False
                await self.broadcast({"type": "GAME_OVER", "game_mode": "tetris", "turn": self.turn})
                return
            self.turn += 1
            tasks = [self.step_tetris_model(m) for m in alive]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            valid = [r for r in results if isinstance(r, dict) and r is not None]
            all_alive = any(self.tetris_games[m].is_alive for m in self.active_tetris_models if m in self.tetris_games)
            await self.broadcast({
                "type": "TICK",
                "game_mode": "tetris",
                "turn": self.turn,
                "events": valid,
                "is_running": self.is_running and all_alive,
                "safety_status": GLOBAL_GEMINI_TRACKER.get_status_summary(),
            })
            if not all_alive:
                self.is_running = False

        elif self.game_mode == "chess":
            # Chess turn
            alive = [m for m in self.active_chess_models if self.chess_games.get(m) and self.chess_games[m].is_alive]
            if not alive:
                self.is_running = False
                await self.broadcast({"type": "GAME_OVER", "game_mode": "chess", "turn": self.turn})
                return
            self.turn += 1
            tasks = [self.step_chess_model(m) for m in alive]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            valid = [r for r in results if isinstance(r, dict) and r is not None]
            all_alive = any(self.chess_games[m].is_alive for m in self.active_chess_models if m in self.chess_games)
            await self.broadcast({
                "type": "TICK",
                "game_mode": "chess",
                "turn": self.turn,
                "events": valid,
                "is_running": self.is_running and all_alive,
                "safety_status": GLOBAL_GEMINI_TRACKER.get_status_summary(),
            })
            if not all_alive:
                self.is_running = False

        elif self.game_mode == "dino":
            # Cyber-Dino turn
            alive = [m for m in self.active_dino_models if self.dino_games.get(m) and self.dino_games[m].is_alive]
            if not alive:
                self.is_running = False
                await self.broadcast({"type": "GAME_OVER", "game_mode": "dino", "turn": self.turn})
                return
            self.turn += 1
            tasks = [self.step_dino_model(m) for m in alive]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            valid = [r for r in results if isinstance(r, dict) and r is not None]
            all_alive = any(self.dino_games[m].is_alive for m in self.active_dino_models if m in self.dino_games)
            await self.broadcast({
                "type": "TICK",
                "game_mode": "dino",
                "turn": self.turn,
                "events": valid,
                "is_running": self.is_running and all_alive,
                "safety_status": GLOBAL_GEMINI_TRACKER.get_status_summary(),
            })
            if not all_alive:
                self.is_running = False

    async def _game_loop(self):
        while self.is_running:
            await self.execute_turn()
            delay = max(0.05, self.step_delay_ms / 1000.0)
            await asyncio.sleep(delay)

    def start(self):
        if not self.is_running:
            self.is_running = True
            self._loop_task = asyncio.create_task(self._game_loop())

    def pause(self):
        self.is_running = False
        if self._loop_task and not self._loop_task.done():
            self._loop_task.cancel()
            self._loop_task = None

    def reset(self, config_updates: Optional[Dict[str, Any]] = None):
        self.pause()
        if config_updates:
            if "game_mode" in config_updates:
                self.game_mode = str(config_updates["game_mode"])
            if "width" in config_updates:
                self.width = int(config_updates["width"])
            if "height" in config_updates:
                self.height = int(config_updates["height"])
            if "seed" in config_updates:
                self.seed = int(config_updates["seed"])
            if "maze_type" in config_updates:
                self.maze_type = str(config_updates["maze_type"])
            if "step_delay_ms" in config_updates:
                self.step_delay_ms = int(config_updates["step_delay_ms"])

        self.log_history.clear()
        self.init_games()


coordinator = ArenaCoordinator()


@app.get("/api/models")
async def get_models():
    ollama_discovered = await discover_ollama_models()
    return {
        "installed_agents": [
            {
                "id": a.model_id,
                "name": a.name,
                "type": a.model_type,
                "color": a.color,
                "active": a.model_id in coordinator.active_snake_models,
            }
            for a in coordinator.snake_agents.values()
        ],
        "tetris_agents": [
            {
                "id": a.model_id,
                "name": a.name,
                "type": a.model_type,
                "color": a.color,
                "active": a.model_id in coordinator.active_tetris_models,
            }
            for a in coordinator.tetris_agents.values()
        ],
        "chess_agents": [
            {
                "id": a.model_id,
                "name": a.name,
                "type": a.model_type,
                "color": a.color,
                "active": a.model_id in coordinator.active_chess_models,
            }
            for a in coordinator.chess_agents.values()
        ],
        "dino_agents": [
            {
                "id": a.model_id,
                "name": a.name,
                "type": a.model_type,
                "color": a.color,
                "active": a.model_id in coordinator.active_dino_models,
            }
            for a in coordinator.dino_agents.values()
        ],
        "safety": GLOBAL_GEMINI_TRACKER.get_status_summary(),
        "ollama_discovered": ollama_discovered,
    }


@app.get("/api/safety")
async def get_safety():
    return JSONResponse(content=GLOBAL_GEMINI_TRACKER.get_status_summary())


@app.post("/api/safety/reset")
async def reset_safety():
    GLOBAL_GEMINI_TRACKER.is_circuit_broken = False
    GLOBAL_GEMINI_TRACKER.trip_reason = None
    GLOBAL_GEMINI_TRACKER.last_status = "ACTIVE_SAFE"
    return JSONResponse(content=GLOBAL_GEMINI_TRACKER.get_status_summary())


@app.get("/api/export-logs")
async def export_logs():
    return JSONResponse(content={
        "game_mode": coordinator.game_mode,
        "seed": coordinator.seed,
        "logs": coordinator.log_history,
    })


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await coordinator.connect_client(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            cmd = json.loads(data)
            action = cmd.get("action")

            if action == "play":
                coordinator.start()
                await coordinator.broadcast({"type": "STATUS_CHANGE", "is_running": True})

            elif action == "pause":
                coordinator.pause()
                await coordinator.broadcast({"type": "STATUS_CHANGE", "is_running": False})

            elif action == "step":
                coordinator.pause()
                await coordinator.execute_turn()

            elif action == "reset":
                coordinator.reset(cmd.get("config"))
                await coordinator.broadcast_full_state()

            elif action == "switch_game":
                target_mode = cmd.get("game_type", "snake")
                coordinator.game_mode = target_mode
                coordinator.reset()
                await coordinator.broadcast_full_state()

            elif action == "update_config":
                cfg = cmd.get("config", {})
                if "step_delay_ms" in cfg:
                    coordinator.step_delay_ms = int(cfg["step_delay_ms"])
                await coordinator.broadcast_full_state()

    except WebSocketDisconnect:
        coordinator.disconnect_client(websocket)
    except Exception:
        coordinator.disconnect_client(websocket)


# Mount frontend static files
DIST_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend_dist")
FRONTEND_DIR = DIST_DIR if os.path.exists(DIST_DIR) else os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

if os.path.exists(os.path.join(FRONTEND_DIR, "assets")):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIR, "assets")), name="assets")

if os.path.exists(os.path.join(FRONTEND_DIR, "css")):
    app.mount("/css", StaticFiles(directory=os.path.join(FRONTEND_DIR, "css")), name="css")

if os.path.exists(os.path.join(FRONTEND_DIR, "js")):
    app.mount("/js", StaticFiles(directory=os.path.join(FRONTEND_DIR, "js")), name="js")


@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


@app.get("/graph")
async def serve_graph_2d():
    graph_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "graphify-out", "graph.html")
    if os.path.exists(graph_path):
        return FileResponse(graph_path)
    return JSONResponse({"error": "graph.html not found"}, status_code=404)


@app.get("/graph3d")
async def serve_graph_3d():
    graph_3d_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "graphify-out", "graph_3d.html")
    if os.path.exists(graph_3d_path):
        return FileResponse(graph_3d_path)
    return JSONResponse({"error": "graph_3d.html not found"}, status_code=404)

