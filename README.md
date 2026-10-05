# 🎮 Multi-Model AI Arena: Snake, Tetris & Chess Benchmark Suite

[![Repository](https://img.shields.io/badge/GitHub-shreytalreja25%2Fsnake--game--benchmark-blue)](https://github.com/shreytalreja25/snake-game-benchmark.git)
[![Backend](https://img.shields.io/badge/FastAPI-0.115+-009688)](https://fastapi.tiangolo.com)
[![Frontend](https://img.shields.io/badge/React_19-Vite_8-61dafb)](https://react.dev)
[![WebSockets](https://img.shields.io/badge/WebSockets-Realtime_60FPS-green)](https://websockets.readthedocs.io)
[![Decision Primitives](https://img.shields.io/badge/TypeSafe_AI-Jev_1.13-00f3ff)](https://openrouter.ai)
[![Google Gemini](https://img.shields.io/badge/Google_Gemini-Flash_Safety_Breaker-4285F4)](https://aistudio.google.com)
[![Open Weight](https://img.shields.io/badge/Laya-ModernBERT_421M-purple)](https://huggingface.co/convaiinnovations/laya)
[![Local LLMs](https://img.shields.io/badge/Ollama-Qwen_3.5_|_Llama_3.1-orange)](https://ollama.com)
[![Chess Engine](https://img.shields.io/badge/python--chess-1.11+-red)](https://python-chess.readthedocs.io)

A real-time, multi-modal benchmarking laboratory evaluating **TypeSafe AI's Jev 1.13 (System-One Decision Primitive)** against **Google Gemini Flash (with automated Safety Circuit Breaker)**, **Laya (Open-Weight ModernBERT Encoder)**, **Local LLMs via Ollama** (`Qwen 3.5 9B`, `Llama 3.1 8B`, `Llama 3.2 1B`), and **algorithmic baselines (A* Pathfinder, Pierre Dellacherie Tetris Solver, Minimax Chess Engine)**.

---

## ⚡ Three Standard Benchmark Arenas

### 1. 🐍 Cyber-Snake Arena
- **Spatial Reasoning & Pathfinding**: Evaluates collision avoidance, flood-fill navigation, and path efficiency towards food.
- **Configurable Grids & Mazes**: 6x6 Micro, 8x8 Standard, 10x10, 12x12, 16x16 with Central Cross, Four Rooms, Labyrinth Corridors, and Random Obstacles.
- **Algorithmic Baseline**: Optimal A* pathfinder with deadlock lookahead.

### 2. 🧱 Cyber-Tetris Arena
- **Lookahead & Surface Heuristics**: 10x20 standard matrix, 7-bag randomizer, candidate placement generation.
- **60 FPS Real-Time Brick Falling**: Smooth real-time brick descent, ghost piece projection, and live command sequence HUD (`SPAWN` $\to$ `ROTATE` $\to$ `SHIFT COL` $\to$ `HARD DROP`).
- **Algorithmic Baseline**: Pierre Dellacherie Heuristic Placement Optimizer.

### 3. ♟️ Cyber-Chess Tactical Arena
- **Tactical Search & Material Calculation**: 8x8 standard chessboard powered by `python-chess`.
- **Concurrent Match Format**: All AI models play as White against the identical deterministic **Minimax Tactical Opponent (Black)** from the exact same seed!
- **Rich Telemetry**: Real-time evaluation score, material balance (pawns differential), check detection, move history, and captured piece tray.
- **Algorithmic Baseline**: 2-ply Minimax engine with Alpha-Beta pruning and piece-square tables.

---

## 🛡️ Google Gemini Flash & Safety Circuit Breaker

The arena integrates **Google Gemini Flash** (`gemini-flash-latest` via Google AI Studio Interactions API / REST):
- **Structured JSON Calling**: Enforces strict JSON decision schema with temperature calibration.
- **Token Ceiling & Circuit Breaker**:
  - Automatically tracks cumulative prompt and candidate tokens via `usageMetadata`.
  - Configurable `GEMINI_MAX_TOKENS` ceiling (default 50,000 tokens).
  - Detects budget exhaustion or HTTP 429 (`RESOURCE_EXHAUSTED` / quota limit).
  - **Graceful Safe Auto-Disable**: When tripped, automatically sets status to `QUOTA_EXHAUSTED (AUTO-DISABLED)` and falls back to deterministic heuristic simulation so the arena continues seamlessly at 60 FPS without crashing!

---

## 🚀 Quickstart

### Prerequisites
- Python 3.10+
- Node.js 18+ (for frontend development)
- (Optional) [Ollama](https://ollama.com) running locally on port `11434`

### Installation
```bash
git clone https://github.com/shreytalreja25/snake-game-benchmark.git
cd snake-game-benchmark

# Setup virtual environment & install requirements
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your keys (GEMINI_API_KEY, TYPESAFE_API_KEY, etc.)
```

### Running the Arena
```bash
# Windows one-click start
run.bat

# Or run manually:
python -m uvicorn backend.server:app --host 0.0.0.0 --port 8000 --reload
```

Open your browser at `http://localhost:8000`.

---

## 🧪 Model Roster & Specifications

| Model | Architecture | Type | Latency (P50) | Cost / 1M Tokens |
|---|---|---|---|---|
| **Jev 1.13** | System-One Primitive | Fast Decision API | **~75 ms** | $0.042 |
| **Gemini Flash** | Multimodal Cloud LLM | Cloud API (Breaker Protected) | **~180 ms** | $0.075 / $0.30 |
| **Laya 421M** | ModernBERT Encoder | Neural Representation | **~50 ms** | $0.00 (Local) |
| **Qwen 3.5 9B** | Dense Generative LLM | Ollama Local | **~2,400 ms** | $0.00 (Local) |
| **Llama 3.1 8B** | Dense Generative LLM | Ollama Local | **~3,100 ms** | $0.00 (Local) |
| **Llama 3.2 1B** | Edge Generative LLM | Ollama Local | **~850 ms** | $0.00 (Local) |
| **Algorithmic Baseline** | A* / Dellacherie / Minimax | Pure Heuristic Search | **< 1 ms** | $0.00 |
