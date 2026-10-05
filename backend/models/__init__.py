"""
Model registry and loader for Snake AI Arena.
"""

from typing import Dict, List, Optional
import httpx
import os

from backend.models.base import BaseSnakeAgent
from backend.models.jev_agent import JevSnakeAgent
from backend.models.laya_agent import LayaSnakeAgent
from backend.models.ollama_agent import OllamaSnakeAgent
from backend.models.heuristic_agent import HeuristicSnakeAgent
from backend.models.gemini_agent import GeminiSnakeAgent, GLOBAL_GEMINI_TRACKER


async def discover_ollama_models(base_url: str = "http://localhost:11434") -> List[Dict[str, str]]:
    """Queries Ollama REST API to dynamically list installed local models."""
    models = []
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            res = await client.get(f"{base_url.rstrip('/')}/api/tags")
            if res.status_code == 200:
                data = res.json()
                for item in data.get("models", []):
                    name = item.get("name", "")
                    if name and not name.startswith("nomic-embed"):  # Skip embeddings
                        models.append({"name": name, "model_id": name})
    except Exception:
        pass

    # Default fallback set if Ollama offline during query
    if not models:
        models = [
            {"name": "lukey03/qwen3.5-9b-abliterated:latest", "model_id": "lukey03/qwen3.5-9b-abliterated:latest"},
            {"name": "llama3.1:latest", "model_id": "llama3.1:latest"},
            {"name": "llama3.2:1b", "model_id": "llama3.2:1b"},
        ]
    return models


def create_default_agents() -> Dict[str, BaseSnakeAgent]:
    """Instantiates default suite of agents."""
    agents: Dict[str, BaseSnakeAgent] = {}

    # 1. TypeSafe Jev System-One
    jev = JevSnakeAgent(
        name="Jev 1.13 (System-1)",
        model_id="typesafe/jev-1.13",
        color="#00f0ff",
    )
    agents[jev.model_id] = jev

    # 2. Google Gemini Flash (Cloud LLM)
    gemini = GeminiSnakeAgent(
        name="Gemini Flash (Google)",
        model_id="gemini-flash-latest",
        color="#4285F4",
    )
    agents[gemini.model_id] = gemini

    # 3. Laya Open-Weight ModernBERT Encoder
    laya = LayaSnakeAgent(
        name="Laya Encoder (421M)",
        model_id="convaiinnovations/laya",
        color="#a855f7",
    )
    agents[laya.model_id] = laya

    # 3. A* Algorithmic Heuristic Baseline
    astar = HeuristicSnakeAgent(
        name="A* Pathfinder (Optimal)",
        model_id="astar_heuristic",
        color="#ec4899",
    )
    agents[astar.model_id] = astar

    # 4. Ollama Primary Models
    qwen = OllamaSnakeAgent(
        name="Qwen 3.5 9B (Ollama)",
        model_id="lukey03/qwen3.5-9b-abliterated:latest",
        color="#10b981",
    )
    agents[qwen.model_id] = qwen

    llama31 = OllamaSnakeAgent(
        name="Llama 3.1 8B (Ollama)",
        model_id="llama3.1:latest",
        color="#f59e0b",
    )
    agents[llama31.model_id] = llama31

    llama32 = OllamaSnakeAgent(
        name="Llama 3.2 1B (Ollama)",
        model_id="llama3.2:1b",
        color="#3b82f6",
    )
    agents[llama32.model_id] = llama32

    return agents
