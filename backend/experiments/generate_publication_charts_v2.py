"""
Publication Figure Generator for Multi-Model AI Arena including OpenAI Decisions API (GPT-6 Luna).
Produces high-resolution 300 DPI figures for research papers and GitHub documentation.
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# Ensure UTF-8 output encoding on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

CHARTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "experiments", "charts"))
os.makedirs(CHARTS_DIR, exist_ok=True)

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['axes.edgecolor'] = '#cbd5e1'
plt.rcParams['axes.linewidth'] = 1.0

# Consistent architectural color palette
COLORS = {
    "A* Pathfinder (Optimal)": "#e84393",
    "Jev 1.13 (System-1)": "#00d2d3",
    "Gemini Flash (Google)": "#4285F4",
    "GPT-6 Luna (Decisions API)": "#10a37f",
    "Laya Encoder (421M)": "#8e44ad",
    "Llama 3.1 8B (Ollama)": "#f39c12",
    "Qwen 3.5 9B (Ollama)": "#2ecc71",
    "Llama 3.2 1B (Ollama)": "#2980b9",
}


def generate_fig1_pareto():
    """Figure 1: The Latency-Accuracy Pareto Frontier across Domains."""
    fig, axes = plt.subplots(1, 3, figsize=(18, 5.5), dpi=300)
    fig.suptitle("Figure 1: The Latency–Accuracy Pareto Frontier with OpenAI Decisions API (GPT-6 Luna)", fontsize=14, fontweight="bold", y=1.03)

    # Snake Data
    snake_data = [
        ("A* Pathfinder (Optimal)", 0.5, 23.0, 0.0),
        ("Jev 1.13 (System-1)", 563.9, 18.0, 1.2),
        ("Gemini Flash (Google)", 203.0, 18.0, 1.0),
        ("GPT-6 Luna (Decisions API)", 1242.9, 18.0, 1.0),
        ("Llama 3.1 8B (Ollama)", 2537.0, 16.0, 2.5),
        ("Qwen 3.5 9B (Ollama)", 2401.0, 9.0, 2.0),
        ("Llama 3.2 1B (Ollama)", 932.0, 2.0, 0.8),
        ("Laya Encoder (421M)", 59.0, 1.0, 0.5),
    ]

    # Tetris Data (Lines cleared)
    tetris_data = [
        ("Jev 1.13 (System-1)", 510.1, 18.0, 1.5),
        ("GPT-6 Luna (Decisions API)", 1039.7, 18.0, 1.2),
        ("Gemini Flash (Google)", 204.0, 17.7, 1.4),
        ("Laya Encoder (421M)", 63.0, 17.0, 1.8),
        ("Qwen 3.5 9B (Ollama)", 2506.0, 17.7, 1.5),
        ("Llama 3.1 8B (Ollama)", 2506.0, 17.7, 1.5),
    ]

    # Chess Data (Moves survived vs Minimax)
    chess_data = [
        ("Gemini Flash (Google)", 199.0, 60.0, 2.0),
        ("Qwen 3.5 9B (Ollama)", 2595.0, 60.0, 2.0),
        ("Llama 3.1 8B (Ollama)", 2595.0, 60.0, 2.0),
        ("Laya Encoder (421M)", 59.0, 56.0, 3.5),
        ("Jev 1.13 (System-1)", 464.2, 49.3, 4.0),
        ("GPT-6 Luna (Decisions API)", 1127.2, 44.0, 5.0),
    ]

    domains = [
        ("Cyber-Snake (Score / Apples)", snake_data, axes[0]),
        ("Cyber-Tetris (Lines Cleared)", tetris_data, axes[1]),
        ("Cyber-Chess (Moves Survived vs Minimax)", chess_data, axes[2]),
    ]

    for title, dataset, ax in domains:
        ax.set_title(title, fontsize=11, fontweight="bold", pad=10)
        ax.set_xscale("log")
        ax.set_xlabel("P50 Decision Latency (ms, log scale)", fontsize=9.5, fontweight="bold")
        ax.set_ylabel("Mean Performance Metric", fontsize=9.5, fontweight="bold")
        ax.grid(True, which="both", linestyle="--", alpha=0.5)

        for name, lat, sc, err in dataset:
            c = COLORS.get(name, "#57606f")
            ax.errorbar(lat, sc, yerr=err, fmt='o', color=c, ecolor=c, elinewidth=1.6, capsize=4, markersize=8.5, alpha=0.9, label=name)
            short_name = name.split()[0]
            if "Luna" in name:
                short_name = "GPT-6 Luna"
            elif "Jev" in name:
                short_name = "Jev 1.13"
            elif "Laya" in name:
                short_name = "Laya"
            elif "Gemini" in name:
                short_name = "Gemini Flash"
            ax.annotate(short_name, (lat, sc), textcoords="offset points", xytext=(5, 4), fontsize=7.5, fontweight="bold", color="#1e293b")

        ax.axvspan(0.1, 100, color='#00d2d3', alpha=0.07, label="Sub-100ms Real-Time Zone")

    handles, labels = axes[0].get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    fig.legend(by_label.values(), by_label.keys(), loc="lower center", ncol=5, bbox_to_anchor=(0.5, -0.09), fontsize=8.5)
    plt.tight_layout()

    out_path = os.path.join(CHARTS_DIR, "fig1_pareto_frontier.png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"✔ Generated: {out_path}")


def generate_fig2_survival():
    """Figure 2: Survival Rates & High-Density Board Performance."""
    fig, ax = plt.subplots(figsize=(10, 5.2), dpi=300)
    fig.suptitle("Figure 2: Maximum Apples Reached & Survival under High Spatial Density (Seed 42)", fontsize=13, fontweight="bold")

    models = [
        "A* Pathfinder (Optimal)",
        "GPT-6 Luna (Decisions API)",
        "Jev 1.13 (System-1)",
        "Gemini Flash (Google)",
        "Llama 3.1 8B (Ollama)",
        "Qwen 3.5 9B (Ollama)",
        "Llama 3.2 1B (Ollama)",
        "Laya Encoder (421M)"
    ]
    scores = [23, 18, 18, 18, 16, 9, 2, 1]
    steps = [156, 129, 133, 129, 117, 65, 28, 8]
    bar_colors = [COLORS.get(m, "#00d2d3") for m in models]

    y_pos = np.arange(len(models))
    bars = ax.barh(y_pos, scores, color=bar_colors, alpha=0.88, edgecolor="#1e293b", height=0.6)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(models, fontsize=9.5, fontweight="bold")
    ax.set_xlabel("Apples Consumed (Final Game Score)", fontsize=10.5, fontweight="bold")
    ax.set_xlim(0, 26)
    ax.grid(axis="x", linestyle="--", alpha=0.5)

    for bar, step in zip(bars, steps):
        w = bar.get_width()
        ax.text(w + 0.4, bar.get_y() + bar.get_height() / 2, f"{int(w)} apples ({step} steps)", va="center", ha="left", fontsize=8.5, fontweight="bold")

    plt.tight_layout()
    out_path = os.path.join(CHARTS_DIR, "fig2_survival_rates.png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"✔ Generated: {out_path}")


def generate_fig3_cost():
    """Figure 3: Inference Cost per 1,000 Game Decisions ($ USD)."""
    fig, ax = plt.subplots(figsize=(9.5, 4.8), dpi=300)
    fig.suptitle("Figure 3: Operational Cost per 1,000 Decisions ($ USD)", fontsize=13, fontweight="bold")

    models = [
        "GPT-6 Luna (Decisions)",
        "Gemini Flash (Cloud LLM)",
        "Jev 1.13 (System-1)",
        "Laya 421M (Offline)",
        "Local Ollama (Ollama)",
        "A* Baseline (Heuristic)"
    ]
    # Costs per 1,000 steps based on token pricing
    costs = [0.0558, 0.00021, 0.00564, 0.00000, 0.00000, 0.00000]
    bar_c = ["#10a37f", "#4285F4", "#00d2d3", "#8e44ad", "#f39c12", "#e84393"]

    bars = ax.bar(models, costs, color=bar_c, width=0.55, edgecolor="#1e293b", alpha=0.9)
    ax.set_ylabel("Cost per 1,000 Decisions ($ USD)", fontsize=10.5, fontweight="bold")
    ax.set_ylim(0, 0.065)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 0.0018, f"${h:.5f}", ha="center", va="bottom", fontsize=8.5, fontweight="bold")

    plt.tight_layout()
    out_path = os.path.join(CHARTS_DIR, "fig3_tokenomics_cost.png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"✔ Generated: {out_path}")


def generate_fig4_latency():
    """Figure 4: Median Latency Across Architectural Paradigms."""
    fig, ax = plt.subplots(figsize=(10.5, 5), dpi=300)
    fig.suptitle("Figure 4: P50 Latency Across Architectural Paradigms (Milliseconds)", fontsize=13, fontweight="bold")

    arch_labels = [
        "A* Baseline",
        "Laya 421M",
        "Gemini Flash",
        "Jev 1.13",
        "Llama 3.2 1B",
        "GPT-6 Luna",
        "Qwen 3.5 9B",
        "Llama 3.1 8B"
    ]
    lat_vals = [0.5, 59.0, 203.0, 563.9, 932.0, 1242.9, 2401.0, 2537.0]
    arch_colors = ["#e84393", "#8e44ad", "#4285F4", "#00d2d3", "#2980b9", "#10a37f", "#2ecc71", "#f39c12"]

    bars = ax.bar(arch_labels, lat_vals, color=arch_colors, width=0.55, edgecolor="#1e293b", alpha=0.9)
    ax.set_yscale("log")
    ax.set_ylabel("P50 Latency (ms, log scale)", fontsize=10.5, fontweight="bold")
    ax.grid(axis="y", which="both", linestyle="--", alpha=0.5)

    ax.axhline(100, color="red", linestyle=":", linewidth=2, label="100ms Real-Time Autonomous Interactive Threshold")
    ax.legend(loc="upper left", fontsize=9.5)

    for bar, val in zip(bars, lat_vals):
        ax.text(bar.get_x() + bar.get_width() / 2, val * 1.25, f"{val:.1f}ms", ha="center", va="bottom", fontsize=8, fontweight="bold")

    plt.tight_layout()
    out_path = os.path.join(CHARTS_DIR, "fig4_latency_comparison.png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"✔ Generated: {out_path}")


def generate_fig5_async():
    """Figure 5: Async Decoupling Speedup (Lock-step vs Independent Coroutines)."""
    fig, ax = plt.subplots(figsize=(9, 4.8), dpi=300)
    fig.suptitle("Figure 5: Execution Pipeline Speedup — Lock-Step vs Decoupled Async Coroutines", fontsize=13, fontweight="bold")

    pipelines = ["Lock-Step Synchronous (Default)", "Decoupled Async (System-1 Parallel)"]
    turn_delays = [2537.0, 59.0]
    bar_c = ["#e74c3c", "#2ecc71"]

    bars = ax.bar(pipelines, turn_delays, color=bar_c, width=0.45, edgecolor="#1e293b", alpha=0.9)
    ax.set_ylabel("Turn Step Execution Delay (ms)", fontsize=10.5, fontweight="bold")
    ax.set_yscale("log")
    ax.grid(axis="y", which="both", linestyle="--", alpha=0.5)

    ax.text(0, turn_delays[0] * 1.2, f"{turn_delays[0]:.0f} ms\n(Blocked on slowest LLM)", ha="center", va="bottom", fontsize=9, fontweight="bold", color="#c0392b")
    ax.text(1, turn_delays[1] * 1.3, f"{turn_delays[1]:.0f} ms\n(43.0x Real-time Speedup)", ha="center", va="bottom", fontsize=9, fontweight="bold", color="#27ae60")

    plt.tight_layout()
    out_path = os.path.join(CHARTS_DIR, "fig5_async_speedup.png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"✔ Generated: {out_path}")


if __name__ == "__main__":
    generate_fig1_pareto()
    generate_fig2_survival()
    generate_fig3_cost()
    generate_fig4_latency()
    generate_fig5_async()
    print("\n[DONE] All 5 publication figures successfully created!")
