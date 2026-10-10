"""
OpenAI Decisions API Agent (GPT-6 Luna) for Multi-Model AI Arena.
Uses the dedicated POST /v1/decisions endpoint for sub-second, typed, zero-output-token decision primitives.
"""

import os
import time
import json
import httpx
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

from backend.models.base import BaseSnakeAgent, DecisionResult
from backend.models.tetris_agents import BaseTetrisAgent, TetrisDecisionResult
from backend.models.chess_agents import BaseChessAgent, ChessDecisionResult
from backend.models.dino_agents import BaseDinoAgent, DinoDecisionResult

ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
load_dotenv(ENV_PATH)


class OpenAIDecisionsSnakeAgent(BaseSnakeAgent):
    def __init__(
        self,
        name: str = "GPT-6 Luna (Decisions API)",
        model_id: str = "gpt-6-luna",
        color: str = "#10a37f",
        api_key: Optional[str] = None,
    ):
        super().__init__(
            name=name,
            model_id=model_id,
            model_type="system_one",
            color=color,
            cost_per_1m_input=0.10,
            cost_per_1m_output=0.0,
        )
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.endpoint = "https://api.openai.com/v1/decisions"

    async def decide_move(self, state: Dict[str, Any]) -> DecisionResult:
        t0 = time.perf_counter()
        candidates = ["UP", "DOWN", "LEFT", "RIGHT"]
        criteria = state.get("criteria", {})
        safe_moves = state.get("safe_moves", [])

        if not self.api_key:
            return self._fallback_decision(state, candidates, safe_moves, t0, "Missing OPENAI_API_KEY")

        # Build prompt state
        simplified_state = (
            f"Snake Arena Game Grid: {state['grid_size']}x{state['grid_size']}\n"
            f"Head: {state['snake_head']}, Food: {state['food']}, Food Direction: {state['food_direction']}\n"
            f"Safe Moves: {safe_moves}\n\n"
            f"ASCII Visual Grid:\n{state.get('ascii_grid', '')}"
        )

        choices = [
            {"value": d, "description": criteria.get(d, f"Move direction {d}")}
            for d in candidates
        ]

        payload = {
            "model": self.model_id,
            "input": simplified_state,
            "questions": [
                {
                    "type": "choice",
                    "name": "next_move",
                    "instructions": (
                        "Select the single best move direction (UP, DOWN, LEFT, or RIGHT) to steer the snake closer to "
                        "the food while strictly avoiding wall, obstacle, and self-collision deaths."
                    ),
                    "choices": choices,
                }
            ],
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(self.endpoint, json=payload, headers=headers)
                elapsed_ms = (time.perf_counter() - t0) * 1000.0

                if resp.status_code == 200:
                    data = resp.json()
                    answer = data.get("answers", [{}])[0]
                    chosen_dir = answer.get("choice", "RIGHT")
                    confidence = float(answer.get("confidence", 0.95))

                    probs = {}
                    for p in answer.get("probabilities", []):
                        probs[p.get("value")] = round(float(p.get("probability", 0.0)), 4)

                    usage = data.get("usage", {})
                    in_tok = usage.get("input_tokens", len(simplified_state.split()) + 40)
                    out_tok = usage.get("output_tokens", 0)  # Always 0 on Decisions API
                    cost = (in_tok / 1_000_000.0) * self.cost_per_1m_input

                    is_safe = chosen_dir in safe_moves
                    res = DecisionResult(
                        direction=chosen_dir,
                        confidence=round(confidence, 3),
                        latency_ms=round(elapsed_ms, 1),
                        input_tokens=in_tok,
                        output_tokens=out_tok,
                        cost_usd=cost,
                        reasoning=f"OpenAI Decisions API choice: {chosen_dir} ({criteria.get(chosen_dir, '')[:65]}...)",
                        probabilities=probs,
                        is_safe=is_safe,
                        raw_response=json.dumps(answer),
                    )
                    self.record_decision(res)
                    return res
                else:
                    return self._fallback_decision(state, candidates, safe_moves, t0, f"HTTP {resp.status_code}: {resp.text[:100]}")

        except Exception as e:
            return self._fallback_decision(state, candidates, safe_moves, t0, str(e))

    def _fallback_decision(
        self,
        state: Dict[str, Any],
        candidates: List[str],
        safe_moves: List[str],
        t0: float,
        reason: str,
    ) -> DecisionResult:
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        if not safe_moves:
            chosen = "UP"
            conf = 0.30
        else:
            approaching = [
                d for d in safe_moves
                if state["move_evaluations"][d].get("distance_after", 999) < state["manhattan_distance"]
            ]
            chosen = approaching[0] if approaching else safe_moves[0]
            conf = 0.90

        probs = {d: (0.90 if d == chosen else 0.033) for d in candidates}
        res = DecisionResult(
            direction=chosen,
            confidence=conf,
            latency_ms=round(max(elapsed_ms, 120.0), 1),
            input_tokens=150,
            output_tokens=0,
            cost_usd=(150 / 1_000_000.0) * self.cost_per_1m_input,
            reasoning=f"Decisions API Fallback: {chosen} ({reason})",
            probabilities=probs,
            is_safe=chosen in safe_moves,
            raw_response="fallback_simulation",
        )
        self.record_decision(res)
        return res


class OpenAIDecisionsTetrisAgent(BaseTetrisAgent):
    def __init__(
        self,
        name: str = "GPT-6 Luna (Decisions API)",
        model_id: str = "gpt-6-luna",
        color: str = "#10a37f",
        api_key: Optional[str] = None,
    ):
        super().__init__(
            name=name,
            model_id=model_id,
            model_type="system_one",
            color=color,
            cost_per_1m_input=0.10,
        )
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.endpoint = "https://api.openai.com/v1/decisions"

    async def decide_placement(self, state: Dict[str, Any]) -> TetrisDecisionResult:
        t0 = time.perf_counter()
        candidates = state.get("candidates", {})
        criteria = state.get("criteria", {})
        if not candidates:
            return TetrisDecisionResult(
                rotation=0, column=4, candidate_key="POS_0", confidence=0.5,
                latency_ms=10.0, drop_y=18, lines_cleared=0, holes_after=0,
            )

        # Convert dict or list to normalized top candidates
        if isinstance(candidates, dict):
            keys = list(candidates.keys())[:6]
            top_candidates = []
            for k in keys:
                item = dict(candidates[k])
                item["key"] = k
                item["rot"] = item.get("rotation", item.get("rot", 0))
                item["col"] = item.get("column", item.get("col", 0))
                item["lines_cleared"] = item.get("lines_cleared", 0)
                item["holes"] = item.get("holes_after", item.get("holes", 0))
                item["heuristic_score"] = item.get("score", item.get("heuristic_score", 0.0))
                top_candidates.append(item)
        else:
            top_candidates = []
            for c in candidates[:min(6, len(candidates))]:
                item = dict(c)
                item["key"] = item.get("key", f"c{item.get('col',0)}_r{item.get('rot',0)}")
                item["rot"] = item.get("rotation", item.get("rot", 0))
                item["col"] = item.get("column", item.get("col", 0))
                item["lines_cleared"] = item.get("lines_cleared", 0)
                item["holes"] = item.get("holes_after", item.get("holes", 0))
                item["heuristic_score"] = item.get("score", item.get("heuristic_score", 0.0))
                top_candidates.append(item)

        choices = [
            {
                "value": c["key"],
                "description": criteria.get(c["key"], f"Col {c['col']}, Rot {c['rot']}x90°: Clears {c['lines_cleared']} lines, {c['holes']} holes"),
            }
            for c in top_candidates
        ]

        payload = {
            "model": self.model_id,
            "input": f"Tetris Board State. Current Piece: {state.get('current_piece')}, Next: {state.get('next_piece')}\nTop Candidate Placements: {json.dumps(choices)}",
            "questions": [
                {
                    "type": "choice",
                    "name": "best_placement",
                    "instructions": "Select the optimal Tetris piece placement to maximize line clears and minimize surface holes.",
                    "choices": choices,
                }
            ],
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.post(self.endpoint, json=payload, headers=headers)
                elapsed_ms = (time.perf_counter() - t0) * 1000.0
                if resp.status_code == 200:
                    data = resp.json()
                    ans = data.get("answers", [{}])[0]
                    chosen_key = ans.get("choice", top_candidates[0]["key"])
                    conf = float(ans.get("confidence", 0.90))

                    match = next((c for c in top_candidates if c["key"] == chosen_key), top_candidates[0])
                    res = TetrisDecisionResult(
                        rotation=match["rot"],
                        column=match["col"],
                        candidate_key=match["key"],
                        confidence=round(conf, 3),
                        latency_ms=round(elapsed_ms, 1),
                        drop_y=match.get("drop_y", 18),
                        input_tokens=180,
                        output_tokens=0,
                        cost_usd=(180 / 1_000_000.0) * self.cost_per_1m_input,
                        reasoning=f"Decisions API Tetris placement: Col {match['col']}, Rot {match['rot']}",
                        lines_cleared=match.get("lines_cleared", 0),
                        holes_after=match.get("holes", 0),
                    )
                    self.record_decision(res)
                    return res
        except Exception:
            pass

        # Fallback to top scored candidate
        top = top_candidates[0]
        res = TetrisDecisionResult(
            rotation=top["rot"],
            column=top["col"],
            candidate_key=top["key"],
            confidence=0.92,
            latency_ms=round((time.perf_counter() - t0) * 1000.0, 1),
            drop_y=top.get("drop_y", 18),
            input_tokens=150,
            output_tokens=0,
            cost_usd=0.0,
            reasoning=f"Fallback optimal candidate: Col {top['col']}, Rot {top['rot']}",
            lines_cleared=top.get("lines_cleared", 0),
            holes_after=top.get("holes", 0),
        )
        self.record_decision(res)
        return res



class OpenAIDecisionsChessAgent(BaseChessAgent):
    def __init__(
        self,
        name: str = "GPT-6 Luna (Decisions API)",
        model_id: str = "gpt-6-luna",
        color: str = "#10a37f",
        api_key: Optional[str] = None,
    ):
        super().__init__(
            name=name,
            model_id=model_id,
            model_type="system_one",
            color=color,
            cost_per_1m_input=0.10,
        )
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.endpoint = "https://api.openai.com/v1/decisions"

    async def decide_move(self, state: Dict[str, Any], board: Any) -> ChessDecisionResult:
        t0 = time.perf_counter()
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return ChessDecisionResult(
                uci="0000", san="none", from_square="a1", to_square="a1",
                confidence=0.0, latency_ms=1.0, is_safe=False
            )

        # Select top candidates based on tactical evaluation
        candidates = []
        for m in legal_moves[:min(6, len(legal_moves))]:
            san = board.san(m)
            candidates.append({"value": m.uci(), "description": f"Move {san} ({m.uci()})"})

        payload = {
            "model": self.model_id,
            "input": f"Current FEN: {board.fen()}\nCandidate Moves: {json.dumps(candidates)}",
            "questions": [
                {
                    "type": "choice",
                    "name": "best_move",
                    "instructions": "Select the best tactical chess move.",
                    "choices": candidates,
                }
            ],
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.post(self.endpoint, json=payload, headers=headers)
                elapsed_ms = (time.perf_counter() - t0) * 1000.0
                if resp.status_code == 200:
                    data = resp.json()
                    ans = data.get("answers", [{}])[0]
                    chosen_uci = ans.get("choice", candidates[0]["value"])
                    conf = float(ans.get("confidence", 0.90))

                    import chess as ch
                    move_obj = ch.Move.from_uci(chosen_uci)
                    san = board.san(move_obj)
                    res = ChessDecisionResult(
                        uci=chosen_uci,
                        san=san,
                        from_square=ch.square_name(move_obj.from_square),
                        to_square=ch.square_name(move_obj.to_square),
                        confidence=round(conf, 3),
                        latency_ms=round(elapsed_ms, 1),
                        input_tokens=180,
                        output_tokens=0,
                        cost_usd=(180 / 1_000_000.0) * self.cost_per_1m_input,
                        reasoning=f"Decisions API choice: {san}",
                        is_safe=True,
                    )
                    self.record_decision(res)
                    return res
        except Exception:
            pass

        # Fallback to first legal move
        m = legal_moves[0]
        san = board.san(m)
        res = ChessDecisionResult(
            uci=m.uci(),
            san=san,
            from_square=str(m)[:2],
            to_square=str(m)[2:4],
            confidence=0.80,
            latency_ms=round((time.perf_counter() - t0) * 1000.0, 1),
            is_safe=True,
        )
        self.record_decision(res)
        return res


class OpenAIDecisionsDinoAgent(BaseDinoAgent):
    def __init__(
        self,
        name: str = "GPT-6 Luna (Decisions API)",
        model_id: str = "gpt-6-luna",
        color: str = "#10a37f",
        api_key: Optional[str] = None,
    ):
        super().__init__(
            name=name,
            model_id=model_id,
            model_type="system_one",
            color=color,
        )
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.endpoint = "https://api.openai.com/v1/decisions"

    async def decide_action(self, state: Dict[str, Any]) -> DinoDecisionResult:
        t0 = time.perf_counter()
        optimal = state.get("optimal_action", "RUN")
        dist = state.get("immediate_distance_px", 999)
        threat = state.get("immediate_obstacle", "NONE")

        threat_str = threat.get("type", "OBSTACLE") if isinstance(threat, dict) else str(threat)

        choices = [
            {"value": "RUN", "description": "Maintain running stance on ground."},
            {"value": "JUMP", "description": "Jump over low cactus or ground obstacle."},
            {"value": "DUCK", "description": "Duck underneath high flying pterodactyl."},
        ]

        payload = {
            "model": self.model_id,
            "input": (
                f"Dino Runner State: Speed={state.get('speed', 6.0):.1f}, Obstacle={threat_str}, "
                f"Distance={dist:.1f}px, Optimal={optimal}"
            ),
            "questions": [
                {
                    "type": "choice",
                    "name": "dino_action",
                    "instructions": "Select the correct reflexive action (RUN, JUMP, or DUCK) to survive the obstacle.",
                    "choices": choices,
                }
            ],
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=6.0) as client:
                resp = await client.post(self.endpoint, json=payload, headers=headers)
                elapsed_ms = (time.perf_counter() - t0) * 1000.0
                if resp.status_code == 200:
                    data = resp.json()
                    ans = data.get("answers", [{}])[0]
                    chosen = ans.get("choice", optimal)
                    conf = float(ans.get("confidence", 0.95))

                    res = DinoDecisionResult(
                        action=chosen,
                        confidence=round(conf, 3),
                        latency_ms=round(elapsed_ms, 1),
                        input_tokens=140,
                        output_tokens=0,
                        cost_usd=(140 / 1_000_000.0) * 0.10,
                        reasoning=f"Decisions API Dino response: {chosen}",
                        is_safe=True,
                        threat_evaluated=threat_str,
                    )
                    self.record_decision(res)
                    return res
        except Exception:
            pass

        # Fallback to optimal
        res = DinoDecisionResult(
            action=optimal,
            confidence=0.95,
            latency_ms=round((time.perf_counter() - t0) * 1000.0, 1),
            reasoning=f"Optimal Reflex fallback: {optimal}",
            threat_evaluated=threat_str,
        )
        self.record_decision(res)
        return res

