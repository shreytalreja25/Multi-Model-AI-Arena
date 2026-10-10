"""
Multi-Model AI Arena: Snake Game Face-Off Benchmark.
Puts OpenAI Decisions API (GPT-6 Luna) head-to-head against:
- TypeSafe AI Jev 1.13 (System-One)
- Laya (Open-Weight ModernBERT Encoder)
- A* Pathfinder (Optimal Algorithmic Baseline)
- Google Gemini Flash (Generative LLM)
- Local Ollama Models (Qwen 3.5 9B, Llama 3.1 8B, Llama 3.2 1B)

Also benchmarked:
1. Traditional Lock-Step Loop (where all models step in lockstep)
2. Decoupled Asynchronous Parallel Loop (where each model runs at maximum native speed independently)
"""

import os
import sys
import time
import json
import asyncio
from typing import Dict, Any, List
from tabulate import tabulate

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from backend.engine.game import SnakeGame
from backend.engine.maze import generate_obstacles
from backend.engine.state_repr import build_model_state
from backend.models import create_default_agents, BaseSnakeAgent


async def run_single_game_decoupled(
    agent: BaseSnakeAgent,
    seed: int,
    grid_size: int = 8,
    max_turns: int = 80,
    maze_type: str = "open",
) -> Dict[str, Any]:
    """Runs a single snake game instance for a model at its own native speed without waiting for other models."""
    obstacles = generate_obstacles(grid_size, grid_size, maze_type, 0.10, seed)
    game = SnakeGame(grid_size, grid_size, seed, obstacles)
    agent.reset_telemetry()

    t_start = time.perf_counter()
    turn = 0
    while turn < max_turns and game.is_alive:
        turn += 1
        state_repr = build_model_state(game)
        dec = await agent.decide_move(state_repr)
        game.step(dec.direction)

    wall_time_s = time.perf_counter() - t_start
    st = game.get_state()
    stats = agent.get_summary_stats()

    return {
        "model_id": agent.model_id,
        "name": agent.name,
        "model_type": agent.model_type,
        "seed": seed,
        "score": st.get("score", 0),
        "steps": st.get("steps", 0),
        "is_alive": game.is_alive,
        "death_reason": game.death_reason,
        "wall_time_s": wall_time_s,
        "p50_latency_ms": stats["p50_latency_ms"],
        "p99_latency_ms": stats["p99_latency_ms"],
        "avg_confidence": stats["avg_confidence"],
        "cost_usd": stats["total_cost_usd"],
        "invalid_moves": stats["invalid_moves"],
        "moves_per_sec": (st.get("steps", 0) / wall_time_s) if wall_time_s > 0 else 0.0,
    }


async def run_faceoff_benchmark(seeds: List[int] = [42, 101, 202], grid_size: int = 8, max_turns: int = 60):
    print("=" * 80)
    print("  CYBER-ARENA SNAKE FACE-OFF: GPT-6 LUNA VS. JEV VS. LAYA VS. BASELINES")
    print("=" * 80)

    agents = create_default_agents()
    models_to_test = [
        "gpt-6-luna",
        "typesafe/jev-1.13",
        "convaiinnovations/laya",
        "astar_heuristic",
        "gemini-flash-latest",
        "lukey03/qwen3.5-9b-abliterated:latest",
        "llama3.1:latest",
    ]

    selected_agents = {m: agents[m] for m in models_to_test if m in agents}

    print(f"\n[*] Evaluating {len(selected_agents)} models across {len(seeds)} game seeds (Max {max_turns} turns)...")
    print(f"[*] Architecture: Decoupled Asynchronous Execution (Models run in parallel without blocking each other)")

    t0_all = time.perf_counter()

    # Launch all model games concurrently across all seeds
    tasks = []
    for seed in seeds:
        for m_id, agent in selected_agents.items():
            tasks.append(run_single_game_decoupled(agent, seed, grid_size, max_turns))

    print(f"[*] Dispatched {len(tasks)} concurrent game sessions to event loop...")
    results = await asyncio.gather(*tasks)

    total_wall_time = time.perf_counter() - t0_all
    print(f"[+] All {len(tasks)} game sessions completed in {total_wall_time:.2f} seconds wall-clock time!\n")

    # Aggregate by model
    model_aggregates = {}
    for r in results:
        m = r["model_id"]
        if m not in model_aggregates:
            model_aggregates[m] = {
                "name": r["name"],
                "model_type": r["model_type"],
                "scores": [],
                "steps": [],
                "wall_times": [],
                "p50_lats": [],
                "costs": [],
                "invalid_moves": [],
                "moves_per_sec": [],
            }
        model_aggregates[m]["scores"].append(r["score"])
        model_aggregates[m]["steps"].append(r["steps"])
        model_aggregates[m]["wall_times"].append(r["wall_time_s"])
        model_aggregates[m]["p50_lats"].append(r["p50_latency_ms"])
        model_aggregates[m]["costs"].append(r["cost_usd"])
        model_aggregates[m]["invalid_moves"].append(r["invalid_moves"])
        model_aggregates[m]["moves_per_sec"].append(r["moves_per_sec"])

    table_data = []
    for m, agg in model_aggregates.items():
        avg_score = sum(agg["scores"]) / len(agg["scores"])
        avg_steps = sum(agg["steps"]) / len(agg["steps"])
        avg_p50 = sum(agg["p50_lats"]) / len(agg["p50_lats"])
        avg_cost = sum(agg["costs"]) / len(agg["costs"])
        total_invalid = sum(agg["invalid_moves"])
        avg_mps = sum(agg["moves_per_sec"]) / len(agg["moves_per_sec"])
        total_steps = sum(agg["steps"])
        safety_rate = ((total_steps - total_invalid) / total_steps * 100.0) if total_steps > 0 else 0.0

        table_data.append([
            agg["name"],
            agg["model_type"],
            f"{avg_score:.1f}",
            f"{avg_steps:.1f}",
            f"{avg_p50:.1f} ms",
            f"{avg_mps:.1f} mv/s",
            f"{safety_rate:.1f}%",
            f"${avg_cost:.6f}",
        ])

    headers = [
        "Model Name",
        "Type",
        "Avg Score (Apples)",
        "Avg Steps",
        "P50 Latency",
        "Throughput",
        "Move Safety",
        "Cost / Game",
    ]

    print(tabulate(table_data, headers=headers, tablefmt="grid"))

    # Save results to json
    out_path = os.path.join(PROJECT_ROOT, "experiments", "gpt6_snake_faceoff_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"summary": table_data, "raw_runs": results, "total_wall_time_s": total_wall_time}, f, indent=2)
    print(f"\n[+] Full benchmark telemetry saved to: {out_path}")


if __name__ == "__main__":
    asyncio.run(run_faceoff_benchmark())
