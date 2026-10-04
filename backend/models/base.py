"""
Base abstract class for all Snake benchmark model agents.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel
import time


class DecisionResult(BaseModel):
    direction: str  # "UP", "DOWN", "LEFT", "RIGHT"
    confidence: float  # 0.0 to 1.0
    latency_ms: float
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    reasoning: Optional[str] = None
    probabilities: Dict[str, float] = {}
    is_safe: bool = True
    raw_response: Optional[str] = None


class BaseSnakeAgent:
    def __init__(
        self,
        name: str,
        model_id: str,
        model_type: str,
        color: str = "#00f0ff",
        cost_per_1m_input: float = 0.0,
        cost_per_1m_output: float = 0.0,
    ):
        self.name = name
        self.model_id = model_id
        self.model_type = model_type  # "system_one", "encoder", "llm", "heuristic"
        self.color = color
        self.cost_per_1m_input = cost_per_1m_input
        self.cost_per_1m_output = cost_per_1m_output

        self.reset_telemetry()

    def reset_telemetry(self):
        self.total_steps: int = 0
        self.latencies_ms: List[float] = []
        self.confidences: List[float] = []
        self.total_input_tokens: int = 0
        self.total_output_tokens: int = 0
        self.total_cost_usd: float = 0.0
        self.invalid_move_attempts: int = 0
        self.last_decision: Optional[DecisionResult] = None

    def record_decision(self, res: DecisionResult):
        self.total_steps += 1
        self.latencies_ms.append(res.latency_ms)
        self.confidences.append(res.confidence)
        self.total_input_tokens += res.input_tokens
        self.total_output_tokens += res.output_tokens
        self.total_cost_usd += res.cost_usd
        if not res.is_safe:
            self.invalid_move_attempts += 1
        self.last_decision = res

    def get_summary_stats(self) -> Dict[str, Any]:
        count = len(self.latencies_ms)
        p50 = float(sorted(self.latencies_ms)[count // 2]) if count else 0.0
        p99_idx = min(count - 1, int(count * 0.99))
        p99 = float(sorted(self.latencies_ms)[p99_idx]) if count else 0.0
        avg_lat = sum(self.latencies_ms) / count if count else 0.0
        avg_conf = sum(self.confidences) / count if count else 0.0

        return {
            "name": self.name,
            "model_id": self.model_id,
            "model_type": self.model_type,
            "color": self.color,
            "total_steps": self.total_steps,
            "avg_latency_ms": round(avg_lat, 2),
            "p50_latency_ms": round(p50, 2),
            "p99_latency_ms": round(p99, 2),
            "avg_confidence": round(avg_conf, 3),
            "input_tokens": self.total_input_tokens,
            "output_tokens": self.total_output_tokens,
            "total_cost_usd": round(self.total_cost_usd, 6),
            "invalid_moves": self.invalid_move_attempts,
            "last_decision": self.last_decision.model_dump() if self.last_decision else None,
        }

    async def decide_move(self, state: Dict[str, Any]) -> DecisionResult:
        raise NotImplementedError
