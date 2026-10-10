import os
import asyncio
from backend.experiments.runner import HeadlessExperimentRunner

os.environ["FAST_BENCHMARK"] = "1"

async def main():
    print("=" * 70)
    print("RUNNING 10-EPISODE BENCHMARK: CYBER-DINO (CHROME DINOSAUR RUNNER)")
    print("=" * 70)
    
    seeds = [42, 43, 44, 45, 46, 47, 48, 49, 50, 51]
    runner = HeadlessExperimentRunner(game_mode="dino", seeds=seeds, max_turns=120, fast_mode=True)
    res = await runner.run()
    
    print("\nBENCHMARK COMPLETED SUCCESSFULLY!")
    print(f"Summary CSV: {res['summary_csv_path']}")
    print(f"JSON Traces: {res['json_path']}")
    print(f"Total Events Logged: {res['total_events']}")
    print("-" * 75)
    print(f"{'Model Name':<30} | {'Score Mean':<10} | {'Surv Rate':<10} | {'P50 Latency':<12} | {'Cost/1k'}")
    print("-" * 75)
    for row in res["summary"]:
        print(f"{row['name']:<30} | {row['score_mean']:<10.1f} | {row['survival_rate_pct']:<10.1f}% | {row['latency_p50_ms']:<10.1f}ms | ${row['cost_per_1k_steps']:.4f}")
    print("-" * 75)

if __name__ == "__main__":
    asyncio.run(main())
