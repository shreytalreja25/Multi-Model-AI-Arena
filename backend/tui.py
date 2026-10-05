"""
Interactive Terminal User Interface (TUI) for Multi-Model AI Arena.
Enables headless batch experimentation, paper-ready statistical analysis,
sped-up terminal simulation replay, and server management.
"""

import os
import sys
import time
import json
import glob
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.live import Live
from rich.align import Align

from backend.experiments.runner import HeadlessExperimentRunner, EXPERIMENTS_DIR
from backend.models.gemini_agent import GLOBAL_GEMINI_TRACKER

console = Console()


def print_banner():
    banner_text = """[bold cyan]
   ██████╗██╗   ██╗██████╗ ███████╗██████╗      █████╗ ██████╗ ███████╗███╗   ██╗ █████╗ 
  ██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗    ██╔══██╗██╔══██╗██╔════╝████╗  ██║██╔══██╗
  ██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝    ███████║██████╔╝█████╗  ██╔██╗ ██║███████║
  ██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗    ██╔══██║██╔══██╗██╔══╝  ██║╚██╗██║██╔══██║
  ╚██████╗   ██║   ██████╔╝███████╗██║  ██║    ██║  ██║██║  ██║███████╗██║ ╚████║██║  ██║
   ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝    ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝╚═╝  ╚═╝
[/bold cyan]
  [bold magenta]HCI Research Laboratory & Scientific Numerical Analysis Console[/bold magenta]
  [dim]Jev 1.13 System-1 • Google Gemini Flash • Laya ModernBERT • Ollama LLMs • Baselines[/dim]
    """
    console.print(Panel(Align.center(banner_text), border_style="cyan", padding=(0, 2)))


def format_summary_table(summary_data: List[Dict[str, Any]], title: str = "Research Paper Statistical Summary") -> Table:
    table = Table(title=f"📊 {title}", header_style="bold cyan", border_style="dim white")
    table.add_column("Rank", justify="center", style="bold yellow")
    table.add_column("Model Architecture", style="bold white")
    table.add_column("Type", style="dim cyan")
    table.add_column("Episodes", justify="center")
    table.add_column("Score (Mean ± Std)", justify="center", style="bold green")
    table.add_column("Median (P50)", justify="center")
    table.add_column("Max", justify="center")
    table.add_column("P50 Lat (ms)", justify="right", style="cyan")
    table.add_column("Avg Lat (ms)", justify="right", style="dim cyan")
    table.add_column("Survival %", justify="center", style="bold magenta")
    table.add_column("Total Cost ($)", justify="right", style="yellow")

    for idx, row in enumerate(summary_data):
        rank = "🥇" if idx == 0 else ("🥈" if idx == 1 else ("🥉" if idx == 2 else f"#{idx + 1}"))
        score_str = f"{row.get('score_mean', 0):.2f} ± {row.get('score_std', 0):.2f}"
        table.add_row(
            rank,
            row.get("name", "Unknown"),
            row.get("model_type", "unknown").upper(),
            str(row.get("episodes", 0)),
            score_str,
            f"{row.get('score_median', 0):.1f}",
            f"{row.get('score_max', 0):.1f}",
            f"{row.get('latency_p50_ms', 0):.1f}",
            f"{row.get('latency_avg_ms', 0):.1f}",
            f"{row.get('survival_rate_pct', 0):.1f}%",
            f"${row.get('total_cost_usd', 0):.6f}",
        )
    return table


async def run_headless_experiment_ui():
    console.print("\n[bold cyan]─── 🚀 Configure Headless Batch Experiment ───[/bold cyan]")
    
    # 1. Select Game Mode
    game_mode = Prompt.ask(
        "Select benchmark domain",
        choices=["snake", "tetris", "chess"],
        default="snake"
    )

    # 2. Episodes / Seeds
    num_episodes = IntPrompt.ask("Number of evaluation episodes (distinct seeds)", default=5)
    base_seed = IntPrompt.ask("Starting seed integer", default=42)
    seeds = [base_seed + i * 59 for i in range(num_episodes)]

    # 3. Max Turns
    default_turns = 100 if game_mode == "snake" else (60 if game_mode == "tetris" else 40)
    max_turns = IntPrompt.ask("Max turns / pieces per episode", default=default_turns)

    # 4. Mode: Live vs Fast
    console.print("\n[bold yellow]Execution Speed Mode:[/bold yellow]")
    console.print("  [cyan]1[/cyan]: Live Model Inference (Queries real Ollama / Gemini / Jev APIs)")
    console.print("  [cyan]2[/cyan]: Fast High-Throughput Simulation (Ultra-fast CPU simulation, zero GPU lag)")
    speed_choice = Prompt.ask("Choose mode", choices=["1", "2"], default="1")

    console.print(f"\n[bold green]Starting {num_episodes}-episode experiment in '{game_mode}'...[/bold green]")
    console.print(f"[dim]Seeds: {seeds}[/dim]\n")

    runner = HeadlessExperimentRunner(
        game_mode=game_mode,
        seeds=seeds,
        max_turns=max_turns,
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold cyan]{task.description}"),
        BarColumn(bar_width=40, complete_style="green", finished_style="bold green"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Evaluating models...", total=num_episodes)

        def on_progress(p):
            progress.update(task, completed=p["completed_episodes"], description=f"Seed {p['current_seed']} ({p['completed_episodes']}/{num_episodes})")

        result = await runner.run(progress_callback=on_progress)

    console.print("\n[bold green]✔ Headless Experiment Complete![/bold green]")
    console.print(f"Total Duration: [bold yellow]{result['total_duration_sec']}s[/bold yellow] | Recorded Events: [bold cyan]{result['total_events']}[/bold cyan]")
    
    # Display table
    table = format_summary_table(result["summary"], title=f"{game_mode.upper()} Benchmark Results (N={num_episodes})")
    console.print(table)

    console.print("\n[bold]Exported Research Artifacts:[/bold]")
    console.print(f"  • JSON Trace: [dim]{result['json_path']}[/dim]")
    console.print(f"  • Summary CSV: [dim cyan]{result['summary_csv_path']}[/dim cyan]")
    console.print(f"  • Step-by-Step CSV: [dim]{result['steps_csv_path']}[/dim]")


def list_experiment_runs() -> List[str]:
    files = glob.glob(os.path.join(EXPERIMENTS_DIR, "run_*.json"))
    files.sort(reverse=True)
    return files


def run_sped_up_replayer_ui():
    runs = list_experiment_runs()
    if not runs:
        console.print("[bold red]No saved experiment runs found in experiments/. Run an experiment first![/bold red]")
        return

    console.print("\n[bold cyan]─── ⚡ Sped-Up Simulation Replayer ───[/bold cyan]")
    console.print("Select a completed experiment to replay at accelerated speed:\n")

    for idx, r_path in enumerate(runs[:8]):
        bname = os.path.basename(r_path)
        sz = os.path.getsize(r_path) / 1024
        console.print(f"  [bold yellow]{idx + 1}[/bold yellow]: {bname} ({sz:.1f} KB)")

    sel = IntPrompt.ask("Choose run number", default=1)
    if sel < 1 or sel > len(runs):
        console.print("[red]Invalid selection.[/red]")
        return

    chosen_file = runs[sel - 1]
    with open(chosen_file, "r", encoding="utf-8") as f:
        run_data = json.load(f)

    g_mode = run_data.get("game_mode", "snake")
    events = run_data.get("events", [])
    if not events:
        console.print("[red]Selected run has no recorded events.[/red]")
        return

    console.print(f"\n[green]Loaded run '{run_data.get('run_id')}': {len(events)} events across {run_data.get('episodes')} episodes.[/green]")
    speed_factor = Prompt.ask("Playback speed multiplier", choices=["1x", "2x", "5x", "10x", "20x", "max"], default="5x")

    delay = 0.05
    if speed_factor == "1x": delay = 0.25
    elif speed_factor == "2x": delay = 0.12
    elif speed_factor == "5x": delay = 0.05
    elif speed_factor == "10x": delay = 0.02
    elif speed_factor == "20x": delay = 0.008
    elif speed_factor == "max": delay = 0.001

    console.print(f"[bold cyan]Simulating moves at {speed_factor} speed (delay: {delay}s)... Press CTRL+C to stop.[/bold cyan]\n")

    # Group events by (seed, turn)
    turns_map: Dict[str, List[Dict[str, Any]]] = {}
    for ev in events:
        k = f"{ev.get('seed', 0)}_T{ev.get('turn', 0)}"
        if k not in turns_map:
            turns_map[k] = []
        turns_map[k].append(ev)

    try:
        for k, turn_events in turns_map.items():
            first_ev = turn_events[0]
            seed_num = first_ev.get("seed")
            turn_num = first_ev.get("turn")

            table = Table(title=f"🎮 [bold cyan]{g_mode.upper()} REPLAY[/bold cyan] | Seed: [yellow]{seed_num}[/yellow] | Turn: [bold green]{turn_num}[/bold green]", border_style="cyan")
            table.add_column("Model", style="bold white")
            table.add_column("Decision", style="bold yellow")
            table.add_column("Score / Metric", justify="center", style="green")
            table.add_column("Latency (ms)", justify="right", style="cyan")
            table.add_column("Reasoning", style="dim white")

            for ev in turn_events:
                dec = ev.get("decision", {})
                st = ev.get("game_state", {})
                score_val = st.get("score") if g_mode == "snake" else (st.get("lines_cleared") if g_mode == "tetris" else st.get("material_diff"))
                move_str = dec.get("san") or dec.get("direction", "")
                table.add_row(
                    ev.get("name", "Unknown"),
                    str(move_str),
                    str(score_val),
                    f"{dec.get('latency_ms', 0):.1f}ms",
                    dec.get("reasoning", "")[:45],
                )

            console.clear()
            console.print(table)
            if delay > 0:
                time.sleep(delay)

        console.print("\n[bold green]✔ Replay Finished.[/bold green]")
        Prompt.ask("Press Enter to return to menu")
    except KeyboardInterrupt:
        console.print("\n[yellow]Replay halted by user.[/yellow]")


def view_paper_tables():
    runs = list_experiment_runs()
    if not runs:
        console.print("[bold red]No saved experiment runs found.[/bold red]")
        return

    console.print("\n[bold cyan]─── 📊 Research Paper Tables ───[/bold cyan]")
    for idx, r_path in enumerate(runs[:5]):
        with open(r_path, "r", encoding="utf-8") as f:
            run_data = json.load(f)
        table = format_summary_table(
            run_data.get("summary", []),
            title=f"Run: {run_data.get('run_id')} ({run_data.get('game_mode', '').upper()} - {run_data.get('episodes')} episodes)"
        )
        console.print(table)
        console.print("")

    Prompt.ask("Press Enter to return to menu")


def inspect_safety_status():
    console.print("\n[bold cyan]─── 🛡️ Google Gemini Safety & Circuit Breaker Status ───[/bold cyan]")
    st = GLOBAL_GEMINI_TRACKER.get_status_summary()

    status_color = "red" if st["is_circuit_broken"] else "green"
    panel_content = f"""
  [bold]Circuit Breaker Status:[/bold] [{status_color}]{st['status']}[/{status_color}]
  [bold]Trip Reason:[/bold] {st['trip_reason'] or 'None (System Operating Safely)'}
  [bold]Token Consumption:[/bold] [bold cyan]{st['total_tokens']:,}[/bold cyan] / [bold]{st['max_tokens']:,}[/bold] ({st['usage_percent']}%)
  [bold]Prompt Tokens:[/bold] {st['prompt_tokens']:,}
  [bold]Candidate Tokens:[/bold] {st['candidate_tokens']:,}
    """
    console.print(Panel(panel_content, title="🛡️ Tokenomics & Circuit Breaker", border_style=status_color))

    if st["is_circuit_broken"]:
        if Confirm.ask("Reset circuit breaker now?"):
            GLOBAL_GEMINI_TRACKER.is_circuit_broken = False
            GLOBAL_GEMINI_TRACKER.trip_reason = None
            GLOBAL_GEMINI_TRACKER.last_status = "ACTIVE_SAFE"
            console.print("[green]✔ Circuit breaker reset to ACTIVE_SAFE.[/green]")

    Prompt.ask("\nPress Enter to return to menu")


async def main_tui():
    while True:
        console.clear()
        print_banner()

        console.print("[bold white]Select an operation:[/bold white]")
        console.print("  [bold cyan]1[/bold cyan]: 🚀 Run Headless Batch Experiment (Paper Numerical Analysis)")
        console.print("  [bold cyan]2[/bold cyan]: ⚡ Sped-Up Simulation Replayer (High-Speed Playback from Logs)")
        console.print("  [bold cyan]3[/bold cyan]: 📊 View Research Paper Summary Tables & Metrics")
        console.print("  [bold cyan]4[/bold cyan]: 🛡️ Inspect Gemini Safety Circuit Breaker & Token Ceiling")
        console.print("  [bold cyan]5[/bold cyan]: 🌐 Server & Web Dashboard Status (http://localhost:8000)")
        console.print("  [bold cyan]6[/bold cyan]: 🚪 Exit\n")

        choice = Prompt.ask("Enter option [1-6]", choices=["1", "2", "3", "4", "5", "6"], default="1")

        if choice == "1":
            await run_headless_experiment_ui()
            Prompt.ask("\nPress Enter to return to menu")
        elif choice == "2":
            run_sped_up_replayer_ui()
        elif choice == "3":
            view_paper_tables()
        elif choice == "4":
            inspect_safety_status()
        elif choice == "5":
            import httpx
            try:
                r = httpx.get("http://localhost:8000/api/models", timeout=1.0)
                if r.status_code == 200:
                    console.print("\n[bold green]✔ Web Server is ONLINE at http://localhost:8000[/bold green]")
                else:
                    console.print("\n[yellow]Server returned status:[/yellow]", r.status_code)
            except Exception:
                console.print("\n[red]Server is offline. You can launch it using 'run.bat' or 'python -m uvicorn backend.server:app'[/red]")
            Prompt.ask("\nPress Enter to return to menu")
        elif choice == "6":
            console.print("[bold cyan]Exiting Cyber Arena TUI. Goodbye![/bold cyan]")
            break


if __name__ == "__main__":
    asyncio.run(main_tui())
