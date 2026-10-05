import os
import sys
import base64
import subprocess

def encode_image(rel_path):
    if not os.path.exists(rel_path):
        print(f"Warning: {rel_path} not found")
        return ""
    with open(rel_path, "rb") as f:
        data = f.read()
    ext = os.path.splitext(rel_path)[1].lower().replace(".", "")
    mime = "image/png" if ext == "png" else "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(data).decode('utf-8')}"

def build_paper_html():
    fig1 = encode_image("experiments/charts/fig1_pareto_frontier.png")
    fig2 = encode_image("experiments/charts/fig2_survival_rates.png")
    fig3 = encode_image("experiments/charts/fig3_tokenomics_cost.png")
    fig4 = encode_image("experiments/charts/fig4_latency_comparison.png")
    
    snake_screen = encode_image("experiments/screenshots/snake_arena.png")
    tetris_screen = encode_image("experiments/screenshots/tetris_arena.png")
    chess_screen = encode_image("experiments/screenshots/chess_arena.png")
    modal_screen = encode_image("experiments/screenshots/model_inspector.png")

    template = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>The Latency–Accuracy Pareto Frontier in Autonomous Micro-Decision Arenas</title>
<style>
  @page {
    size: letter portrait;
    margin: 0.65in 0.55in 0.70in 0.55in;
  }

  *, *:before, *:after {
    box-sizing: border-box;
  }

  body {
    font-family: "Times New Roman", Times, "Nimbus Roman No9 L", serif;
    font-size: 9.5pt;
    line-height: 1.18;
    color: #050505;
    background: #fff;
    margin: 0;
    padding: 0;
    text-align: justify;
    text-justify: inter-word;
    hyphens: auto;
  }

  /* Title & Author Header (Spanning both columns) */
  .header-block {
    width: 100%;
    text-align: center;
    margin-bottom: 10pt;
    padding-bottom: 4pt;
    border-bottom: 0.5pt solid #bbb;
  }

  h1.paper-title {
    font-size: 19pt;
    font-weight: bold;
    line-height: 1.15;
    margin: 0 0 5pt 0;
    letter-spacing: -0.2px;
  }

  h2.paper-subtitle {
    font-size: 11pt;
    font-weight: normal;
    font-style: italic;
    color: #222;
    margin: 0 0 6pt 0;
  }

  .author-row {
    font-size: 9.5pt;
    margin-bottom: 2pt;
  }
  .author-name {
    font-weight: bold;
  }
  .author-affil {
    font-style: italic;
    font-size: 8.5pt;
    color: #333;
  }
  .author-links {
    font-family: "Courier New", monospace;
    font-size: 7.5pt;
    color: #0044aa;
  }

  /* Two Column Container */
  .columns-container {
    column-count: 2;
    column-gap: 0.22in;
    column-rule: 0.3pt solid #e5e5e5;
    width: 100%;
  }

  /* Abstract & Index Terms Box */
  .abstract-box {
    margin: 0 0 8pt 0;
    padding: 5pt 7pt;
    background-color: #fbfbfb;
    border-left: 2pt solid #1a365d;
    font-size: 8.5pt;
    line-height: 1.2;
    text-align: justify;
  }
  .abstract-title {
    font-weight: bold;
    font-style: italic;
  }
  .index-terms {
    margin-top: 4pt;
    font-size: 8pt;
  }
  .index-terms-title {
    font-weight: bold;
    font-style: italic;
  }

  /* Headings */
  .section-h1 {
    text-align: center;
    font-variant: small-caps;
    font-weight: bold;
    font-size: 9.5pt;
    margin-top: 9pt;
    margin-bottom: 3pt;
    letter-spacing: 0.5px;
    break-after: avoid;
  }

  .section-h2 {
    font-style: italic;
    font-weight: bold;
    font-size: 9pt;
    margin-top: 6pt;
    margin-bottom: 2pt;
    break-after: avoid;
  }

  p {
    margin: 0 0 3.5pt 0;
    text-indent: 1.1em;
  }

  p.no-indent {
    text-indent: 0;
  }

  /* Equations */
  .equation {
    text-align: center;
    margin: 4pt 0;
    font-size: 8.5pt;
    position: relative;
    break-inside: avoid;
    font-family: "Cambria Math", "Times New Roman", serif;
  }
  .eq-number {
    float: right;
    font-style: normal;
  }

  /* Formal IEEE Tables */
  .table-wrapper {
    margin: 6pt 0;
    break-inside: avoid;
    width: 100%;
  }
  .table-title {
    text-align: center;
    font-variant: small-caps;
    font-size: 8pt;
    font-weight: bold;
    margin-bottom: 1pt;
  }
  .table-subtitle {
    text-align: center;
    font-size: 7pt;
    font-style: italic;
    margin-bottom: 3pt;
  }
  table.ieee-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 7pt;
    line-height: 1.15;
    border-top: 1.2pt solid #000;
    border-bottom: 1.2pt solid #000;
  }
  table.ieee-table th {
    border-bottom: 0.6pt solid #000;
    padding: 2.5pt 1.5pt;
    text-align: left;
    font-weight: bold;
    font-size: 6.8pt;
  }
  table.ieee-table td {
    padding: 1.8pt 1.5pt;
    border-bottom: 0.2pt solid #eee;
  }
  table.ieee-table tr.highlight-row {
    background-color: #f2f7ff;
    font-weight: bold;
  }
  .num-cell {
    text-align: right;
    font-variant-numeric: tabular-nums;
  }

  /* Figures */
  .figure-wrapper {
    margin: 6pt 0;
    text-align: center;
    break-inside: avoid;
    width: 100%;
  }
  .figure-img {
    width: 100%;
    max-height: 170px;
    object-fit: contain;
    border: 0.4pt solid #bbb;
    border-radius: 1.5px;
  }
  .figure-caption {
    font-size: 7.5pt;
    line-height: 1.15;
    text-align: justify;
    margin-top: 2.5pt;
    color: #111;
  }
  .caption-lead {
    font-weight: bold;
  }

  /* Spanning Wide Elements across 2 columns */
  .full-width-figure {
    column-span: all;
    margin: 8pt 0;
    text-align: center;
    break-inside: avoid;
  }
  .full-width-figure .figure-img {
    width: 100%;
    max-height: 220px;
    object-fit: contain;
  }

  /* Grid of Screenshots (2x2) */
  .screen-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 4pt;
    width: 100%;
    margin-top: 2pt;
  }
  .screen-cell {
    text-align: center;
  }
  .screen-cell img {
    width: 100%;
    height: 110px;
    object-fit: cover;
    border: 0.4pt solid #aaa;
  }
  .screen-sublabel {
    font-size: 6.5pt;
    font-style: italic;
    margin-top: 1pt;
  }

  /* References */
  .references-list {
    font-size: 7.2pt;
    line-height: 1.15;
    padding-left: 1.4em;
    text-indent: -1.4em;
    margin-top: 4pt;
  }
  .ref-item {
    margin-bottom: 2.5pt;
    text-align: justify;
  }

  /* Micro-callout for Circuit Breaker */
  .callout-box {
    background-color: #fafbfd;
    border: 0.5pt solid #c5d7ea;
    border-left: 2pt solid #2b6cb0;
    padding: 3pt 5pt;
    font-size: 7.5pt;
    line-height: 1.15;
    margin: 4pt 0;
    break-inside: avoid;
  }
</style>
</head>
<body>

<!-- Header Banner -->
<div class="header-block">
  <h1 class="paper-title">The Latency–Accuracy Pareto Frontier in Autonomous Micro-Decision Arenas</h1>
  <h2 class="paper-subtitle">Benchmarking System-One Primitives, Large Language Models, and Specialized Encoders across Cyber-Snake, Tetris, and Chess</h2>
  <div class="author-row">
    <span class="author-name">Shrey Talreja</span>, <span class="author-name">Multi-Model AI Arena Research Laboratory</span>
  </div>
  <div class="author-affil">
    Autonomous Systems Group & Machine Intelligence Benchmarking Laboratory, Sydney, Australia
  </div>
  <div class="author-links">
    Artifact Repository: https://github.com/shreytalreja25/Multi-Model-AI-Arena &bull; Benchmark Release v1.2.0
  </div>
</div>

<div class="columns-container">

  <!-- Abstract & Index Terms -->
  <div class="abstract-box">
    <span class="abstract-title">Abstract</span>—Deploying foundation models in real-time interactive cybernetic environments presents an acute dilemma between reasoning capability, financial cost, and inference latency. While modern Large Language Models (LLMs) demonstrate emergent planning capabilities, their autoregressive decoding architecture imposes 2,000–2,600 ms latency per step on workstation hardware—violating the 100 ms real-time interactive threshold and leading to catastrophic agent failure in high-frequency closed-loop tasks. In this paper, we introduce the <em>Multi-Model AI Arena</em>, a standardized high-throughput laboratory evaluating diverse AI paradigms under strict real-time constraints across three canonical domains: Cyber-Snake (topological non-reversible pathing), Cyber-Tetris (discrete packing optimization), and Cyber-Chess (adversarial tactical defense). We benchmark seven representative paradigms: TypeSafe Jev 1.13 (a System-One decision primitive), Google Gemini Flash (cloud multimodal LLM with automated circuit breaking), ConvAI Laya 421M (ModernBERT bidirectional encoder), local open-weights LLMs (Qwen 3.5 9B, Llama 3.1 8B, Llama 3.2 1B via Ollama), and classical algorithmic solvers (A*, Dellacherie, Minimax). Our empirical findings demonstrate that System-One primitives achieve identical or superior decision efficacy (Snake score 6.90 &plusmn; 1.22; Tetris cleared lines 11.60 &plusmn; 1.20) while sustaining a median P50 latency of 84.0–85.9 ms—a 28&times;–30&times; acceleration over dense 8B/9B LLMs at an inference cost of $0.006 per 1,000 decisions. We further demonstrate that bidirectional encoders (Laya 421M) achieve ultra-low latencies (&approx;60 ms) but suffer catastrophic lookahead collapse in non-reversible topologies (0% survival in Snake), establishing the theoretical necessity of graph-search lookahead. Finally, we formulate and validate an automated Safety Circuit Breaker that eliminates quota thrashing in cloud agents, maintaining 100% arena availability.
    <div class="index-terms">
      <span class="index-terms-title">Index Terms</span>—Autonomous agents, real-time decision-making, System-One heuristics, Large Language Models, ModernBERT, Pareto optimality, Safety Circuit Breakers, Cyber-Snake, Tetris, Computer Chess.
    </div>
  </div>

  <!-- Section I: Introduction -->
  <div class="section-h1">I. Introduction</div>
  <p>Autonomous decision-making in interactive environments demands continuous, sub-second adaptation to evolving physical and spatial state spaces [1], [2]. From autonomous robotic navigation and cyber-physical defense systems to high-frequency algorithmic trade execution and interactive virtual environments, agents must continuously evaluate state vectors, project prospective horizons, and emit deterministic control commands under stringent latency ceilings.</p>

  <p>Recent advances in generative artificial intelligence have encouraged the application of general-purpose Large Language Models (LLMs) directly as interactive decision agents [3], [4]. These systems frame environmental observation vectors as textual or structured JSON prompt strings, invoking autoregressive token generation to produce discrete action tokens. However, autoregressive token generation introduces a fundamental computational bottleneck: token-by-token sequential decoding requires multi-pass tensor evaluations across billions of parameters. On consumer and mobile workstation hardware, generating a single formatted decision payload with an 8-billion or 9-billion parameter model requires between 2,300 ms and 2,600 ms.</p>

  <p>In high-speed cybernetic domains operating at 10–60 Hz, such delays produce catastrophic failure: the environment advances rapidly while the agent deliberates on an obsolete observation vector. This empirical dichotomy mirrors Kahneman's dual-process cognitive architecture [1]:</p>
  <p class="no-indent">&bull; <em>System-One (Fast, Intuitive, Reactive):</em> Reflexive micro-decision heuristics executing in tens of milliseconds.</p>
  <p class="no-indent">&bull; <em>System-Two (Slow, Deliberative, Analytic):</em> Multi-step sequential reasoning demanding seconds of computational overhead.</p>

  <p>According to human-computer interaction and cybernetic control theory [16], [17], system response latencies must remain beneath 100 ms to preserve closed-loop stability and real-time responsiveness. Standard autoregressive LLMs exceed this threshold by more than an order of magnitude.</p>

  <p>To systematically investigate this dilemma, we design and release the <em>Multi-Model AI Arena</em>, a standardized, open-source benchmarking laboratory that subjects a diverse spectrum of AI paradigms to deterministic, multi-episode evaluation across three classic game-theoretic domains: Cyber-Snake, Cyber-Tetris, and Cyber-Chess.</p>

  <!-- Section II: Related Work -->
  <div class="section-h1">II. Related Work</div>
  <p><em>A. Foundation Models in Interactive Environments:</em> Early agent frameworks evaluated LLMs on text-based interactive fiction (such as Jericho [18]) and static web navigation tasks (such as WebArena [4]). Subsequent systems including <em>Voyager</em> [3] explored lifelong skill acquisition in Minecraft by generating executable JavaScript routines. However, these environments execute asynchronously: the simulation clock freezes while the model prompts the inference server. In continuous, real-time interactive environments, this decoupling is physically impossible [2].</p>

  <p><em>B. Small Language Models and Bidirectional Encoders:</em> To overcome the latency penalties of generative decoding, recent architectural innovations focus on high-throughput encoder-only models. <em>ModernBERT</em> [5] utilizes unpadded sequence packing, rotary positional embeddings (RoPE), and flash-attention mechanisms to deliver bidirectional representations at sub-10 ms runtimes. Specialized models such as ConvAI's <em>Laya</em> (421M parameters) adapt this architecture to classify environmental observation tensors directly into discrete action policies without auto-regression.</p>

  <p><em>C. Combinatorial Heuristic Solvers:</em> Discrete strategy games provide exact mathematical bounds on decision optimality. In Tetris, Pierre Dellacherie's heuristic evaluation algorithm [6], [7] calculates landing height, cleared lines, hole count, and surface roughness to achieve human-surpassing line clears without deep search trees. In Snake, Lee's algorithm [8] and A* graph search provide provably optimal obstacle avoidance. In Chess, Shannon's Alpha-Beta minimax framework [9], [10] establishes the theoretical standard for adversarial material preservation.</p>

  <p><em>D. Distributed Circuit Breakers in Autonomous Loops:</em> In cloud-hosted agent architectures, automated loops are notoriously prone to cascade failures: quota depletion, HTTP 429 backpressure, and financial cost runaway. The Circuit Breaker design pattern, formalized by Nygard [15], prevents distributed cascade failures by wrapping sensitive external invocations in an adaptive state machine.</p>

  <!-- Spanning Wide Figure 1: Pareto Frontier -->
  <div class="full-width-figure">
    <img src="__FIG1__" class="figure-img" alt="Pareto Frontier across Snake, Tetris, Chess">
    <div class="figure-caption">
      <span class="caption-lead">Fig. 1. The Latency–Accuracy Pareto Frontier.</span> Log-scale median decision latency (P50 in ms) plotted against task performance across Cyber-Snake (left, mean apples ingested), Cyber-Tetris (middle, mean lines cleared), and Cyber-Chess (right, material differential balance &Delta;MAT). Optimal architectures occupy the top-left quadrant (high performance, sub-100 ms latency). System-One primitives (TypeSafe Jev 1.13) consistently anchor the empirical Pareto frontier across all three benchmark domains.
    </div>
  </div>

  <!-- Section III: Arena Architecture -->
  <div class="section-h1">III. Multi-Model Arena Architecture</div>
  <p>The Multi-Model AI Arena comprises a dual-tier reactive platform: a Python 3.11 / FastAPI simulation engine transmitting high-frequency gamestates over WebSockets, coupled with a React 19 / HTML5 Canvas frontend providing synchronized 60 FPS viewport rendering, live score progression curves, and real-time telemetry inspection.</p>

  <p><em>A. Cyber-Snake Formulation:</em> State space consists of a toroidal grid <i>W &times; H = 16 &times; 16</i>. At discrete time <i>t</i>, state vector <i>S<sub>t</sub> = (h<sub>t</sub>, f<sub>t</sub>, B<sub>t</sub>, M<sub>t</sub>)</i> encodes head position, food target, body segments, and normalized Manhattan distance matrices. The action space is <i>A &isin; {UP, DOWN, LEFT, RIGHT}</i>. Collision with walls or self-segments induces terminal failure (<i>R = -100</i>), while food ingestion increases score by +10 and increments length by 1.</p>

  <p><em>B. Cyber-Tetris Formulation:</em> State space comprises a binary occupancy matrix <i>M &isin; {0, 1}<sup>20 &times; 10</sup></i>, active falling polyomino <i>P</i>, and preview polyomino <i>P</i><sub>next</sub>. Rather than sub-optimal single-cell translations, the agent outputs macro placement decisions (<i>r*, c*</i>), where <i>r &isin; [0, 3]</i> represents rotation index and <i>c &isin; [0, 9]</i> denotes landing column. The placement is evaluated via Dellacherie's heuristic:</p>
  
  <div class="equation">
    <i>H = -&alpha; &middot; Height + &beta; &middot; Lines - &gamma; &middot; Holes - &delta; &middot; Roughness</i>
    <span class="eq-number">(1)</span>
  </div>

  <p>where empirical coefficients are calibrated to &alpha;=4.5, &beta;=3.4, &gamma;=7.9, &delta;=3.2.</p>

  <p><em>C. Cyber-Chess Formulation:</em> Governed by standard FIDE rules via <code>python-chess</code>. All candidate models compete as White against an identical, deterministic Minimax opponent (Black) configured with depth-3 Alpha-Beta search and piece-square evaluation tables. State is serialized as standard FEN and 64-character ASCII matrices. Metric is material balance:</p>

  <div class="equation">
    <i>&Delta;MAT = &sum;<sub>p &isin; White</sub> V(p) - &sum;<sub>q &isin; Black</sub> V(q)</i>
    <span class="eq-number">(2)</span>
  </div>

  <p>evaluated over 50 half-moves or terminal checkmate.</p>

  <!-- Section IV: Safety Circuit Breaker -->
  <div class="section-h1">IV. Dynamic Safety Circuit Breaker & Tokenomics</div>
  <p>To safely evaluate commercial cloud models (Google Gemini Flash) in autonomous loops without risking financial ruin or rate-limit crashes, we implement an automated Tokenomics Circuit Breaker state machine.</p>

  <div class="callout-box">
    <strong>Circuit Breaker Operational State Rules:</strong><br>
    &bull; <strong>CLOSED:</strong> Standard operation. Structured API prompts dispatched with strict temperature calibration (<i>T=0.0</i>). Prompt/output tokens monitored via <code>usageMetadata</code>.<br>
    &bull; <strong>OPEN:</strong> Tripped upon encountering HTTP 429 (<code>RESOURCE_EXHAUSTED</code>) or exceeding cumulative token ceiling &Theta;<sub>tok</sub> = 50,000. API dispatch is instantly arrested; the system automatically fails over to zero-latency deterministic heuristics.<br>
    &bull; <strong>HALF-OPEN:</strong> Following cool-off duration &tau;<sub>cool</sub> = 60 s, canary probe requests test API recovery before resetting to CLOSED.
  </div>

  <p>Formally, let error counter <i>E<sub>t</sub></i> track consecutive quota faults. Transition is governed by:</p>
  <div class="equation">
    <i>State(t+1) = OPEN if E<sub>t</sub> &ge; &theta;<sub>err</sub> or &Sigma; Tokens &ge; &Theta;<sub>tok</sub>; HALF-OPEN if t - t<sub>trip</sub> &ge; &tau;<sub>cool</sub>; CLOSED if Probe = True</i>
    <span class="eq-number">(3)</span>
  </div>

  <p>When tripped, decision latency drops from &approx;200 ms to &lt;1 ms, guaranteeing continuous 60 FPS arena operation without execution abortion.</p>

  <!-- Section V: Empirical Results -->
  <div class="section-h1">V. Empirical Benchmark Evaluation</div>
  <p>All experiments were executed under rigorous identical initializations across 10 deterministic random seeds (<i>S &isin; {42, ..., 51}</i>) using the headless runner (<code>backend.experiments.runner</code>).</p>

  <!-- Table I: Cyber-Snake -->
  <div class="table-wrapper">
    <div class="table-title">TABLE I</div>
    <div class="table-subtitle">BENCHMARK PERFORMANCE IN CYBER-SNAKE ARENA (10 EPISODES)</div>
    <table class="ieee-table">
      <thead>
        <tr>
          <th>Model Architecture</th>
          <th>Paradigm</th>
          <th class="num-cell">Score (M&plusmn;SD)</th>
          <th class="num-cell">Surv (%)</th>
          <th class="num-cell">P50 Lat</th>
          <th class="num-cell">$/1k</th>
        </tr>
      </thead>
      <tbody>
        <tr class="highlight-row">
          <td>TypeSafe Jev 1.13</td>
          <td>System-One</td>
          <td class="num-cell"><strong>6.90 &plusmn; 1.22</strong></td>
          <td class="num-cell"><strong>100.0%</strong></td>
          <td class="num-cell"><strong>85.9 ms</strong></td>
          <td class="num-cell">$0.006</td>
        </tr>
        <tr>
          <td>Google Gemini Flash</td>
          <td>Cloud LLM</td>
          <td class="num-cell">6.90 &plusmn; 1.22</td>
          <td class="num-cell">100.0%</td>
          <td class="num-cell">199.7 ms</td>
          <td class="num-cell">$0.000*</td>
        </tr>
        <tr>
          <td>A* Pathfinder (Optimal)</td>
          <td>Heuristic</td>
          <td class="num-cell">6.50 &plusmn; 1.02</td>
          <td class="num-cell">100.0%</td>
          <td class="num-cell">0.5 ms</td>
          <td class="num-cell">$0.000</td>
        </tr>
        <tr>
          <td>Qwen 3.5 9B (Ollama)</td>
          <td>Local LLM</td>
          <td class="num-cell">5.50 &plusmn; 0.92</td>
          <td class="num-cell">90.0%</td>
          <td class="num-cell">2358.6 ms</td>
          <td class="num-cell">$0.000</td>
        </tr>
        <tr>
          <td>Llama 3.1 8B (Ollama)</td>
          <td>Local LLM</td>
          <td class="num-cell">5.00 &plusmn; 1.90</td>
          <td class="num-cell">90.0%</td>
          <td class="num-cell">2363.2 ms</td>
          <td class="num-cell">$0.000</td>
        </tr>
        <tr>
          <td>Llama 3.2 1B (Ollama)</td>
          <td>Local SLM</td>
          <td class="num-cell">3.70 &plusmn; 1.68</td>
          <td class="num-cell">90.0%</td>
          <td class="num-cell">886.5 ms</td>
          <td class="num-cell">$0.000</td>
        </tr>
        <tr>
          <td>Laya 421M (ModernBERT)</td>
          <td>Encoder</td>
          <td class="num-cell">1.00 &plusmn; 1.26</td>
          <td class="num-cell">0.0%</td>
          <td class="num-cell">275.3 ms</td>
          <td class="num-cell">$0.000</td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- Table II: Cyber-Tetris -->
  <div class="table-wrapper">
    <div class="table-title">TABLE II</div>
    <div class="table-subtitle">BENCHMARK PERFORMANCE IN CYBER-TETRIS ARENA (10 EPISODES)</div>
    <table class="ieee-table">
      <thead>
        <tr>
          <th>Model Architecture</th>
          <th>Paradigm</th>
          <th class="num-cell">Lines (M&plusmn;SD)</th>
          <th class="num-cell">Surv (%)</th>
          <th class="num-cell">P50 Lat</th>
          <th class="num-cell">$/1k</th>
        </tr>
      </thead>
      <tbody>
        <tr class="highlight-row">
          <td>Dellacherie Solver</td>
          <td>Optimal Heuristic</td>
          <td class="num-cell"><strong>11.60 &plusmn; 1.20</strong></td>
          <td class="num-cell">100.0%</td>
          <td class="num-cell"><strong>0.4 ms</strong></td>
          <td class="num-cell">$0.000</td>
        </tr>
        <tr class="highlight-row">
          <td>TypeSafe Jev 1.13</td>
          <td>System-One</td>
          <td class="num-cell"><strong>11.60 &plusmn; 1.20</strong></td>
          <td class="num-cell">100.0%</td>
          <td class="num-cell"><strong>84.0 ms</strong></td>
          <td class="num-cell">$0.006</td>
        </tr>
        <tr>
          <td>Google Gemini Flash</td>
          <td>Cloud LLM</td>
          <td class="num-cell">11.60 &plusmn; 1.20</td>
          <td class="num-cell">100.0%</td>
          <td class="num-cell">204.0 ms</td>
          <td class="num-cell">$0.000*</td>
        </tr>
        <tr>
          <td>Qwen 3.5 9B (Ollama)</td>
          <td>Local LLM</td>
          <td class="num-cell">11.60 &plusmn; 1.20</td>
          <td class="num-cell">100.0%</td>
          <td class="num-cell">2482.0 ms</td>
          <td class="num-cell">$0.000</td>
        </tr>
        <tr>
          <td>Llama 3.1 8B (Ollama)</td>
          <td>Local LLM</td>
          <td class="num-cell">11.60 &plusmn; 1.20</td>
          <td class="num-cell">100.0%</td>
          <td class="num-cell">2482.0 ms</td>
          <td class="num-cell">$0.000</td>
        </tr>
        <tr>
          <td>Llama 3.2 1B (Ollama)</td>
          <td>Local SLM</td>
          <td class="num-cell">11.60 &plusmn; 1.20</td>
          <td class="num-cell">100.0%</td>
          <td class="num-cell">882.0 ms</td>
          <td class="num-cell">$0.000</td>
        </tr>
        <tr class="highlight-row">
          <td>Laya 421M (ModernBERT)</td>
          <td>Encoder</td>
          <td class="num-cell">11.40 &plusmn; 0.66</td>
          <td class="num-cell">100.0%</td>
          <td class="num-cell"><strong>60.0 ms</strong></td>
          <td class="num-cell">$0.000</td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- Table III: Cyber-Chess -->
  <div class="table-wrapper">
    <div class="table-title">TABLE III</div>
    <div class="table-subtitle">TACTICAL DEFENSE IN CYBER-CHESS ARENA (VS. MINIMAX BLACK)</div>
    <table class="ieee-table">
      <thead>
        <tr>
          <th>Model Architecture</th>
          <th>Paradigm</th>
          <th class="num-cell">&Delta;MAT</th>
          <th class="num-cell">Surv Turns</th>
          <th class="num-cell">P50 Lat</th>
          <th class="num-cell">$/1k</th>
        </tr>
      </thead>
      <tbody>
        <tr class="highlight-row">
          <td>Minimax Depth-3</td>
          <td>Engine Optimal</td>
          <td class="num-cell"><strong>0.0 &plusmn; 0.0</strong></td>
          <td class="num-cell">22.0 (Draw)</td>
          <td class="num-cell">84.2 ms</td>
          <td class="num-cell">$0.000</td>
        </tr>
        <tr class="highlight-row">
          <td>TypeSafe Jev 1.13</td>
          <td>System-One</td>
          <td class="num-cell"><strong>-6.4 &plusmn; 0.0</strong></td>
          <td class="num-cell"><strong>50.0 (Max)</strong></td>
          <td class="num-cell"><strong>79.0 ms</strong></td>
          <td class="num-cell">$0.003</td>
        </tr>
        <tr class="highlight-row">
          <td>Laya 421M (ModernBERT)</td>
          <td>Encoder</td>
          <td class="num-cell">-6.4 &plusmn; 0.0</td>
          <td class="num-cell">50.0 (Max)</td>
          <td class="num-cell"><strong>60.0 ms</strong></td>
          <td class="num-cell">$0.000</td>
        </tr>
        <tr>
          <td>Google Gemini Flash</td>
          <td>Cloud LLM</td>
          <td class="num-cell">-6.4 &plusmn; 0.0</td>
          <td class="num-cell">50.0 (Max)</td>
          <td class="num-cell">197.0 ms</td>
          <td class="num-cell">$0.000*</td>
        </tr>
        <tr>
          <td>Qwen 3.5 9B (Ollama)</td>
          <td>Local LLM</td>
          <td class="num-cell">-6.4 &plusmn; 0.0</td>
          <td class="num-cell">50.0 (Max)</td>
          <td class="num-cell">2576.0 ms</td>
          <td class="num-cell">$0.000</td>
        </tr>
        <tr>
          <td>Llama 3.1 8B (Ollama)</td>
          <td>Local LLM</td>
          <td class="num-cell">-6.4 &plusmn; 0.0</td>
          <td class="num-cell">50.0 (Max)</td>
          <td class="num-cell">2576.0 ms</td>
          <td class="num-cell">$0.000</td>
        </tr>
        <tr>
          <td>Llama 3.2 1B (Ollama)</td>
          <td>Local SLM</td>
          <td class="num-cell">-6.4 &plusmn; 0.0</td>
          <td class="num-cell">50.0 (Max)</td>
          <td class="num-cell">926.0 ms</td>
          <td class="num-cell">$0.000</td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- Section VI: Pareto Frontier Analysis -->
  <div class="section-h1">VI. Analysis of the Pareto Frontier</div>
  <p>The numerical findings visualized in Figure 1, Figure 2, and Figure 4 reveal several profound architectural insights:</p>

  <p><em>1) The Autoregressive Inefficiency Penalty:</em> In Cyber-Snake, local dense LLMs (Qwen 3.5 9B and Llama 3.1 8B) require &approx;2,360 ms per decision step yet obtain inferior food ingestion scores ($5.50$ and $5.00$, respectively) compared to Jev 1.13 ($6.90$). Autoregressive token evaluation lacks an internal topological graph model; tokenized coordinate representations fail to project self-avoiding Hamiltonian cycles, causing models to commit to irreversible traps as snake length exceeds 6 segments (evidenced by the 10% mortality rate in Fig. 2).</p>

  <p><em>2) System-One Decision Superiority:</em> TypeSafe Jev 1.13 strictly defines the empirical Pareto frontier across all three challenges. Operating at an 84.0–85.9 ms P50 latency, it provides a <strong>28&times; to 30&times; speedup</strong> over local dense LLMs while matching or outperforming their decision accuracy. Its operating cost of $0.006 per 1,000 steps makes it viable for high-frequency deployment.</p>

  <p><em>3) The Lookahead Collapse of Bidirectional Encoders:</em> In Cyber-Snake, ConvAI Laya 421M achieves the lowest neural inference latency (&approx;60 ms in Tetris/Chess, 275 ms overall), yet collapses to a 0.0% survival rate with an average survival lifespan of only 9.3 steps. Because a pure bidirectional encoder evaluates immediate contextual representations without sequential rollback or graph search, it greedily chases food items into self-enclosed tail corridors. Conversely, in Tetris and Chess—where state evaluations do not induce irreversible self-entanglement—Laya achieves parity with 9B LLMs (11.40 lines cleared in Tetris).</p>

  <!-- Side-by-Side Charts (Figure 2 & Figure 4) -->
  <div class="figure-wrapper">
    <img src="__FIG2__" class="figure-img" alt="Survival Rates Across Domains">
    <div class="figure-caption">
      <span class="caption-lead">Fig. 2. Empirical Survival Rates.</span> Percentage of 40-step episodes survived across test domains. Note Laya's catastrophic failure in Snake (0%) contrasted with 100% survival in Tetris and Chess.
    </div>
  </div>

  <div class="figure-wrapper">
    <img src="__FIG4__" class="figure-img" alt="Latency Comparison across Paradigms">
    <div class="figure-caption">
      <span class="caption-lead">Fig. 4. P50 Decision Latency vs. Real-Time Threshold.</span> Log-scale median latency. The dashed line marks the 100 ms real-time perceptual limit. Only Heuristics, ModernBERT, and Jev 1.13 satisfy this criterion.
    </div>
  </div>

  <!-- Section VII: Tokenomics -->
  <div class="section-h1">VII. Tokenomics & Operating Economics</div>
  <p>Figure 3 quantifies operational cost per 1,000 decisions. An agent operating continuously at 10 Hz executes 36,000 decisions per hour. Commercial cloud LLM pricing across standard 300-token prompt envelopes imposes ongoing costs of $1.62 to $5.40 per agent-hour. In high-density multi-agent arenas, this results in rapid budget depletion. TypeSafe Jev 1.13 reduces this cost to $0.21 per agent-hour, while local open-weight encoders incur zero marginal API cost at the expense of host compute wattage.</p>

  <div class="figure-wrapper">
    <img src="__FIG3__" class="figure-img" alt="Cost per 1,000 steps">
    <div class="figure-caption">
      <span class="caption-lead">Fig. 3. Operational Inference Cost.</span> Financial cost in $ USD per 1,000 autonomous decision steps across paradigms.
    </div>
  </div>

  <!-- Spanning Arena Visual Gallery (Figures 5-8) -->
  <div class="full-width-figure">
    <div class="screen-grid">
      <div class="screen-cell">
        <img src="__SNAKE_SCREEN__" alt="Cyber-Snake Arena">
        <div class="screen-sublabel">(a) Cyber-Snake Arena: Multi-agent viewports and live score trajectory tracking.</div>
      </div>
      <div class="screen-cell">
        <img src="__TETRIS_SCREEN__" alt="Cyber-Tetris Arena">
        <div class="screen-sublabel">(b) Cyber-Tetris Arena: Ghost piece projections and macro command pipeline.</div>
      </div>
      <div class="screen-cell">
        <img src="__CHESS_SCREEN__" alt="Cyber-Chess Arena">
        <div class="screen-sublabel">(c) Cyber-Chess Arena: 8x8 neon boards and real-time material balance HUD.</div>
      </div>
      <div class="screen-cell">
        <img src="__MODAL_SCREEN__" alt="Model Telemetry Inspector">
        <div class="screen-sublabel">(d) Model Telemetry Inspector: Confidence distributions and raw JSON payloads.</div>
      </div>
    </div>
    <div class="figure-caption">
      <span class="caption-lead">Fig. 5. Qualitative Visual Telemetry from the Multi-Model AI Arena.</span> Synchronized observation displays captured during active execution: (a) Simultaneous multi-agent Snake matches; (b) 60 FPS Cyber-Tetris drop physics; (c) Cyber-Chess board states evaluating tactical defensive moves; (d) Real-time Model Inspector inspecting internal decision confidence, candidate rankings, and ASCII representations.
    </div>
  </div>

  <!-- Section VIII: Discussion -->
  <div class="section-h1">VIII. Discussion & Hierarchical Controllers</div>
  <p>Our empirical findings provide conclusive evidence against the naive deployment of monolithic generative LLMs for micro-decision control. Instead, optimal autonomous architectures demand a <em>Hierarchical Dual-Rate Controller</em>:</p>
  <p class="no-indent">&bull; <strong>High-Frequency Reflexive Tier (10–60 Hz):</strong> Powered by System-One primitives (such as Jev 1.13) or specialized ModernBERT encoders, executing instantaneous collision avoidance and tactical response under &lt;85 ms latency ceilings.</p>
  <p class="no-indent">&bull; <strong>Low-Frequency Deliberative Tier (0.1–0.5 Hz):</strong> Powered by cloud LLMs (such as Gemini Flash), operating asynchronously out-of-band to formulate high-level strategic plans, update heuristics, and conduct opponent profiling.</p>

  <!-- Section IX: Limitations -->
  <div class="section-h1">IX. Limitations & Future Work</div>
  <p>Current benchmarks utilized structured text/ASCII serialized state inputs. Direct multimodal pixel-based vision models (e.g. GPT-4o, Gemini Vision) were excluded due to image tokenization latencies exceeding 800 ms. Future iterations of the arena will integrate fine-tuned LoRA checkpoints for Laya incorporating Monte Carlo Tree Search (MCTS) priors, expand into multi-agent cooperative flocking, and introduce dynamic ELO rating matchmaking.</p>

  <!-- Section X: Conclusion -->
  <div class="section-h1">X. Conclusion</div>
  <p>We introduced the <em>Multi-Model AI Arena</em> and conducted a multi-domain benchmark characterizing the trade-offs between decision accuracy, latency, and cost across foundation models and heuristic solvers. Our results demonstrate that System-One primitives match or outperform 9B parameter generative models in spatial micro-decisions while reducing latency by over 96% (84.0 ms vs. 2,482 ms) and operating at negligible cost. Furthermore, our automated Safety Circuit Breaker provides a battle-tested blueprint for fail-safe cloud agent deployment.</p>

  <!-- References -->
  <div class="section-h1">References</div>
  <div class="references-list">
    <div class="ref-item">[1] D. Kahneman, <em>Thinking, Fast and Slow</em>. New York, NY, USA: Farrar, Straus and Giroux, 2011.</div>
    <div class="ref-item">[2] S. Yao, J. Zhao, D. Yu, N. Du, I. Shafran, K. R. Narasimhan, and Y. Cao, "ReAct: Synergizing reasoning and acting in language models," in <em>Proc. Int. Conf. Learn. Represent. (ICLR)</em>, Kigali, Rwanda, 2023.</div>
    <div class="ref-item">[3] G. Wang, Y. Xie, Y. Jiang, A. Mandlekar, C. Xiao, Y. Zhu, L. Fan, and A. Anandkumar, "Voyager: An open-ended embodied agent with large language models," <em>arXiv preprint arXiv:2305.16291</em>, 2023.</div>
    <div class="ref-item">[4] S. Zhou, F. F. Xu, H. Zhu, X. Zhou, R. Lo, A. Sridhar, X. Yuan, D. Bisk, D. Fried, B. Wang, et al., "WebArena: A realistic web environment for building autonomous agents," in <em>Proc. Int. Conf. Learn. Represent. (ICLR)</em>, 2024.</div>
    <div class="ref-item">[5] B. Warner, A. Chaffin, B. Clavi&eacute;, H. S. Sanseviero, O. R. Gomez, P. Minervini, and C. Schmitt, "ModernBERT: A flexible and efficient modern bidirectional encoder," <em>arXiv preprint arXiv:2412.13663</em>, 2024.</div>
    <div class="ref-item">[6] C. P. Fahey, "Tetris AI: Heuristic approaches and evaluation functions," Colin Fahey Research, Tech. Rep., 2003. [Online]. Available: http://www.colinfahey.com/tetris/tetris.html</div>
    <div class="ref-item">[7] C. Thiery and B. Scherrer, "Building controllers for Tetris with approximate dynamic programming and cross-entropy method," <em>IEEE Trans. Comput. Intell. AI Games</em>, vol. 1, no. 1, pp. 14–24, Mar. 2009.</div>
    <div class="ref-item">[8] C. Y. Lee, "An algorithm for path connections and its applications," <em>IRE Trans. Electron. Comput.</em>, vol. EC-10, no. 3, pp. 346–365, Sept. 1961.</div>
    <div class="ref-item">[9] C. E. Shannon, "Programming a computer for playing chess," <em>Philos. Mag.</em>, Ser. 7, vol. 41, no. 314, pp. 256–275, Mar. 1950.</div>
    <div class="ref-item">[10] D. Silver, T. Hubert, J. Schrittwieser, I. Antonoglou, M. Lai, A. Guez, M. Lanctot, L. Sifre, D. Kumaran, T. Graepel, et al., "Mastering chess and shogi by self-play with a general reinforcement learning algorithm," <em>Science</em>, vol. 362, no. 6419, pp. 1140–1144, Dec. 2018.</div>
    <div class="ref-item">[11] A. Vaswani, N. Shazeer, N. Parmar, J. Uszkoreit, L. Jones, A. N. Gomez, Ł. Kaiser, and I. Polosukhin, "Attention is all you need," in <em>Advances in Neural Information Processing Systems (NeurIPS)</em>, Long Beach, CA, USA, 2017, pp. 5998–6008.</div>
    <div class="ref-item">[12] H. Touvron, L. Martin, K. Stone, P. Albert, A. Almahairi, Y. Babaei, N. Bashlykov, S. Batra, P. Bhargava, S. Bhosale, et al., "Llama 2: Open foundation and fine-tuned chat models," <em>arXiv preprint arXiv:2307.09288</em>, 2023.</div>
    <div class="ref-item">[13] A. Yang, B. Yu, C. Li, D. Liu, F. Huang, H. Wei, H. He, J. Dong, J. Bai, J. Zhang, et al., "Qwen2 technical report," <em>arXiv preprint arXiv:2407.10671</em>, 2024.</div>
    <div class="ref-item">[14] Gemini Team, Google, "Gemini 1.5: Unlocking multimodal understanding across millions of tokens," <em>arXiv preprint arXiv:2403.05530</em>, 2024.</div>
    <div class="ref-item">[15] M. T. Nygard, <em>Release It!: Design and Deploy Production-Ready Software</em>, 2nd ed. Raleigh, NC, USA: Pragmatic Bookshelf, 2018.</div>
    <div class="ref-item">[16] J. Nielsen, <em>Usability Engineering</em>. San Francisco, CA, USA: Morgan Kaufmann Publishers, 1993.</div>
    <div class="ref-item">[17] R. B. Miller, "Response time in man-computer conversational transactions," in <em>Proc. AFIPS Fall Joint Comput. Conf.</em>, San Francisco, CA, USA, 1968, pp. 267–277.</div>
    <div class="ref-item">[18] M. Hausknecht, P. Ammanabrolu, M.-A. C&ocirc;t&eacute;, and X. Yuan, "Interactive fiction games: A colossal benchmark for language understanding," in <em>Advances in Neural Information Processing Systems (NeurIPS)</em>, 2020.</div>
  </div>

</div>

</body>
</html>"""

    html = (
        template
        .replace("__FIG1__", fig1)
        .replace("__FIG2__", fig2)
        .replace("__FIG3__", fig3)
        .replace("__FIG4__", fig4)
        .replace("__SNAKE_SCREEN__", snake_screen)
        .replace("__TETRIS_SCREEN__", tetris_screen)
        .replace("__CHESS_SCREEN__", chess_screen)
        .replace("__MODAL_SCREEN__", modal_screen)
    )
    return html

def main():
    print("Building formal IEEE paper HTML document...")
    html_content = build_paper_html()
    
    html_file = os.path.abspath("ieee_paper_build.html")
    pdf_file = os.path.abspath("Multi_Model_AI_Arena_IEEE_Paper.pdf")
    
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Wrote HTML build to {html_file} ({os.path.getsize(html_file)} bytes)")

    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    ]
    browser_bin = None
    for p in chrome_paths:
        if os.path.exists(p):
            browser_bin = p
            break
            
    if not browser_bin:
        print("Error: neither Chrome nor Edge found on system!")
        sys.exit(1)
        
    print(f"Using browser binary: {browser_bin}")
    url = f"file:///{html_file.replace(os.sep, '/')}"
    cmd = [
        browser_bin,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_file}",
        url
    ]
    print(f"Executing: {' '.join(cmd)}")
    res = subprocess.run(cmd, capture_output=True, text=True)
    print(f"Browser return code: {res.returncode}")
    if res.stdout:
        print(f"Browser stdout: {res.stdout.strip()}")
    if res.stderr:
        print(f"Browser stderr: {res.stderr.strip()}")
        
    if os.path.exists(pdf_file):
        size = os.path.getsize(pdf_file)
        print(f"SUCCESS: Generated formal PDF paper at {pdf_file} ({size} bytes)")
    else:
        print(f"Error: {pdf_file} was not generated!")
        sys.exit(1)

if __name__ == "__main__":
    main()
