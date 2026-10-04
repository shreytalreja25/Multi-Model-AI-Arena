# 🐍 Cyber-Snake AI Benchmark: System-One Decision Models vs. Local Generative LLMs

[![Repository](https://img.shields.io/badge/GitHub-shreytalreja25%2Fsnake--game--benchmark-blue)](https://github.com/shreytalreja25/snake-game-benchmark.git)
[![Backend](https://img.shields.io/badge/FastAPI-0.115+-009688)](https://fastapi.tiangolo.com)
[![WebSockets](https://img.shields.io/badge/WebSockets-Realtime_Telemetry-green)](https://websockets.readthedocs.io)
[![Decision Primitives](https://img.shields.io/badge/TypeSafe_AI-Jev_1.13-00f3ff)](https://openrouter.ai)
[![Open Weight](https://img.shields.io/badge/Laya-ModernBERT_421M-purple)](https://huggingface.co/convaiinnovations/laya)
[![Local LLMs](https://img.shields.io/badge/Ollama-Qwen_3.5_|_Llama_3.1-orange)](https://ollama.com)

A high-performance, real-time multi-model benchmarking laboratory evaluating **TypeSafe AI's Jev (System-One Decision Primitive)** against **Laya (Open-Weight ModernBERT Encoder)**, **Local LLMs via Ollama** (`Qwen 3.5 9B`, `Llama 3.1 8B`, `Llama 3.2 1B`), and an **optimal algorithmic baseline (A* + Flood-Fill)** in spatial reasoning and reactive decision-making.

---

## ⚡ Executive Summary: The Spatial Reasoning Frontier

Traditional generative LLMs incur huge latency penalties (2,000–4,500 ms/step) and heavy token generation overhead for real-time robotic or game loop decisions. **System-One Decision Models (Jev & Laya)** deliver structured decision primitives in **sub-100ms** with zero generative token bloat.

This benchmark provides a strictly controlled, synchronized arena where models face **identical pseudo-random seeds**, board dimensions, and apple spawn sequences to measure:
1. **Decision Latency (P50/P99)**: Milliseconds required per move.
2. **Survival & Path Efficiency**: Apples eaten vs. steps survived before wall/body collisions.
3. **Spatial Calibration**: Reported model confidence vs. empirical survival rates.
4. **Tokenomics & Cost Efficiency**: API expenditure per 1,000 game steps ($0.042/1M tokens for Jev vs. $0.00 for local models).

---

## 🖥️ Architecture & High-Level HCI Features

```
┌────────────────────────────────────────────────────────────────────────┐
│                        CYBER-SNAKE BENCHMARK LAB                       │
├──────────────────────┬─────────────────────────┬───────────────────────┤
│  ⚡ JEV 1.13 (Sys-1) │  🧠 LAYA (Encoder)       │  🎯 A* PATHFINDER     │
│  [8x8 Canvas View]   │  [8x8 Canvas View]      │  [8x8 Canvas View]    │
│  Latency: 82ms       │  Latency: 52ms          │  Latency: 0.6ms       │
│  Score: 8  Step: 34  │  Score: 6  Step: 28     │  Score: 11 Step: 42   │
├──────────────────────┼─────────────────────────┼───────────────────────┤
│  🤖 QWEN 3.5 9B      │  🦙 LLAMA 3.1 8B        │  🐣 LLAMA 3.2 1B      │
│  [8x8 Canvas View]   │  [8x8 Canvas View]      │  [8x8 Canvas View]    │
│  Latency: 2,420ms    │  Latency: 3,110ms       │  Latency: 890ms       │
│  Score: 7  Step: 29  │  Score: 5  Step: 24     │  Score: 3  Step: 14 (X)│
├──────────────────────┴─────────────────────────┴───────────────────────┤
│  📊 Live Leaderboard | 🔬 Model Brain & Radar Inspector | ⚙️ Config    │
│  📟 Streaming Telemetry Log Streamer & Interactive Hacker CLI Console │
└────────────────────────────────────────────────────────────────────────┘
```

- **Smooth 60 FPS HTML5 Canvas Viewports**: Glowing snake heads, decaying luminous body segments, pulsating holographic apples, and death forensics crosshairs.
- **Identical Seed Guarantee**: Every active model plays on the identical maze layout, starting snake vector, and apple sequence for direct 1-to-1 scientific comparability.
- **Model Brain & Decision Inspector**:
  - Live **Directional Probability Bars** (`UP`, `DOWN`, `LEFT`, `RIGHT`).
  - Spatial **Hazard Matrix** (Safe moves vs. Wall/Body/Neck collisions).
  - Raw **ASCII Board Map** and Verbatim JSON decision output.
- **Hacker Streaming Terminal**:
  - Real-time color-coded stdout logs with turn, latency, token count, and reasoning.
  - Interactive CLI command line (`help`, `play`, `pause`, `step`, `seed <n>`, `grid <size>`, `export`).
  - One-click **JSON** and **CSV** export for research papers.
- **Web Audio API Sound Engine**:
  - Synthesized retro-futuristic soundscapes for apple consumption, collision alarms, and arena ticks (zero external audio file dependencies).

---

## 🛠️ Quickstart

### 1. Prerequisites
- Python 3.10+
- (Optional) [Ollama](https://ollama.com) running locally with models installed (`ollama pull lukey03/qwen3.5-9b-abliterated:latest`, `ollama pull llama3.1:latest`, `ollama pull llama3.2:1b`).
- OpenRouter API key (for live Jev System-One evaluation).

### 2. Installation
```bash
git clone https://github.com/shreytalreja25/snake-game-benchmark.git
cd snake-game-benchmark

# Copy and edit environment variables
cp .env.example .env
# Add your OPENROUTER_API_KEY in .env

# Install backend dependencies
pip install -r requirements.txt
```

### 3. Launch
On Windows:
```bash
run.bat
```
Or manually:
```bash
python -m uvicorn backend.server:app --host 0.0.0.0 --port 8000 --reload
```

Open your browser to:
👉 **`http://localhost:8000`**

---

## 🔬 Benchmark Methodology

### 1. Jev System-One (`typesafe/jev-1.13`)
- Evaluated via native System-One decision primitives (`typesafe_sdk.TypeSafeClient`).
- Receives structured coordinate state and choice criteria descriptions.
- Delivers sub-100ms low-latency decisions with zero generative token overhead.

### 2. Laya ModernBERT (`convaiinnovations/laya`)
- Open-weight 421M parameter ModernBERT encoder running locally on CPU/GPU.
- Sub-60ms encoder routing without autoregressive generation.

### 3. Ollama Generative LLMs
- Receives spatial ASCII board maps, coordinates, and criteria over local REST API.
- Generates JSON move directives with reasoning chains.

### 4. Algorithmic Baseline (A* + Flood-Fill)
- Deterministic graph search prioritizing shortest path to food when reachable flood space $\ge \frac{L}{2}$, otherwise maximizing survival flood space (tail chasing).
- Ground-truth scientific control.

---

## 📜 Citation
```bibtex
@article{talreja2026snake,
  title={Cyber-Snake AI Benchmark: Evaluating System-One Decision Models vs. Frontier LLMs in Real-Time Spatial Navigation},
  author={Talreja, Shrey},
  journal={GitHub Repository: shreytalreja25/snake-game-benchmark},
  year={2026}
}
```
