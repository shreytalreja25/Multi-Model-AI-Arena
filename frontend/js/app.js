/**
 * Multi-Model AI Arena Master Controller (Snake & Tetris).
 * Supports dual-game real-time switching, independent renderers, telemetry, and live inspector.
 */

class ArenaApp {
  constructor() {
    this.ws = null;
    this.gameMode = "snake"; // "snake" or "tetris"
    this.models = [];
    this.modelsMap = {};
    this.renderers = {}; // model_id -> SnakeCanvasRenderer or TetrisCanvasRenderer
    this.lastEvents = {};

    this.turn = 0;
    this.isRunning = false;
    this.config = {
      game_mode: "snake",
      width: 8,
      height: 8,
      seed: 42,
      maze_type: "open",
      step_delay_ms: 300,
    };

    // Submodules
    this.audio = new CyberAudioEngine();
    this.terminal = new HackerTerminalLogger(document.getElementById("terminalBody"));
    this.inspector = new ModelInspectorModal(document.getElementById("inspectorModal"));
    this.charts = new TelemetryCharts(
      document.getElementById("latencyCanvas"),
      document.getElementById("scoreCanvas")
    );

    this.initUI();
    this.connectWebSocket();
  }

  connectWebSocket() {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const host = window.location.host || "localhost:8000";
    const wsUrl = `${protocol}//${host}/ws`;

    this.updateStatusBadge("connecting");
    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => this.updateStatusBadge("connected");
    this.ws.onclose = () => {
      this.updateStatusBadge("disconnected");
      setTimeout(() => this.connectWebSocket(), 2000);
    };
    this.ws.onerror = () => this.updateStatusBadge("disconnected");

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.handleMessage(data);
      } catch (e) {
        console.error("Failed to parse WS message:", e);
      }
    };
  }

  updateStatusBadge(status) {
    const badge = document.getElementById("statusBadge");
    const text = document.getElementById("statusText");
    if (!badge || !text) return;

    badge.className = "status-badge";
    if (status === "connected") {
      text.textContent = "ONLINE [WS 8000]";
    } else if (status === "connecting") {
      badge.classList.add("disconnected");
      text.textContent = "CONNECTING...";
    } else {
      badge.classList.add("disconnected");
      text.textContent = "OFFLINE (RETRYING)";
    }
  }

  handleMessage(msg) {
    if (msg.type === "FULL_STATE") {
      this.gameMode = msg.game_mode || "snake";
      this.turn = msg.turn || 0;
      this.isRunning = msg.is_running || false;
      this.config = msg.config || this.config;
      this.models = msg.models || [];
      this.modelsMap = {};
      this.models.forEach(m => { this.modelsMap[m.model_id] = m; });

      this.syncGameModeUI();
      this.updateHeaderStats();
      this.renderViewports();
      this.updateLeaderboard();
      this.updatePlayPauseButton();

    } else if (msg.type === "TICK") {
      this.turn = msg.turn;
      this.isRunning = msg.is_running;
      this.updateHeaderStats();
      this.updatePlayPauseButton();

      let anyScore = false;
      let anyCrashed = false;

      (msg.events || []).forEach(ev => {
        this.lastEvents[ev.model_id] = ev;
        if (this.modelsMap[ev.model_id]) {
          this.modelsMap[ev.model_id].game_state = ev.game_state;
          this.modelsMap[ev.model_id].telemetry = ev.telemetry;
        }

        // Terminal logging
        this.terminal.addEvent(ev);

        // Chart latency
        if (ev.decision?.latency_ms !== undefined) {
          this.charts.recordStep(ev.model_id, ev.decision.latency_ms);
        }

        // Audio cues
        if (this.gameMode === "snake") {
          if (ev.decision?.eats_food) anyScore = true;
        } else {
          if (ev.decision?.lines_cleared > 0) anyScore = true;
        }

        if (!ev.game_state?.is_alive && ev.decision?.is_safe === false) {
          anyCrashed = true;
        }

        // Render viewport
        const r = this.renderers[ev.model_id];
        if (r) {
          r.render(ev.game_state, ev.color, ev.game_state.is_alive, ev.game_state.death_reason);
        }
        this.updateCardHUD(ev.model_id, ev.game_state, ev.telemetry, ev.decision);

        // Update inspector if focused
        if (this.inspector.currentModelId === ev.model_id) {
          this.inspector.update(this.modelsMap[ev.model_id], ev);
        }
      });

      if (anyCrashed) this.audio.playCrash();
      else if (anyScore) this.audio.playFood();
      else this.audio.playStep();

      this.updateLeaderboard();
      this.charts.drawLatencyChart(this.modelsMap);
      this.charts.drawScoreChart(this.models);

    } else if (msg.type === "STATUS_CHANGE") {
      this.isRunning = msg.is_running;
      this.updatePlayPauseButton();

    } else if (msg.type === "GAME_OVER") {
      this.isRunning = false;
      this.updatePlayPauseButton();
      this.audio.playCrash();
    }
  }

  send(cmd) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(cmd));
    }
  }

  initUI() {
    // Game Mode Tabs (Snake vs Tetris)
    const tabSnake = document.getElementById("tabSnake");
    const tabTetris = document.getElementById("tabTetris");

    if (tabSnake && tabTetris) {
      tabSnake.onclick = () => {
        if (this.gameMode !== "snake") {
          this.gameMode = "snake";
          this.audio.playStart();
          this.send({ action: "switch_game", game_type: "snake" });
        }
      };
      tabTetris.onclick = () => {
        if (this.gameMode !== "tetris") {
          this.gameMode = "tetris";
          this.audio.playStart();
          this.send({ action: "switch_game", game_type: "tetris" });
        }
      };
    }

    // Play/Pause button
    const btnPlay = document.getElementById("btnPlay");
    if (btnPlay) {
      btnPlay.onclick = () => {
        if (this.isRunning) {
          this.send({ action: "pause" });
        } else {
          this.audio.playStart();
          this.send({ action: "play" });
        }
      };
    }

    // Step button
    const btnStep = document.getElementById("btnStep");
    if (btnStep) {
      btnStep.onclick = () => this.send({ action: "step" });
    }

    // Reset button
    const btnReset = document.getElementById("btnReset");
    if (btnReset) {
      btnReset.onclick = () => {
        this.send({ action: "reset", config: this.gatherConfigFromUI() });
        this.charts.clear();
        this.terminal.clear();
      };
    }

    // Speed slider
    const speedSlider = document.getElementById("speedSlider");
    const speedVal = document.getElementById("speedVal");
    if (speedSlider) {
      speedSlider.oninput = (e) => {
        const val = parseInt(e.target.value);
        if (speedVal) speedVal.textContent = `${val}ms`;
        this.send({ action: "update_config", config: { step_delay_ms: val } });
      };
    }

    // Grid size selector
    const gridSizeSelect = document.getElementById("gridSizeSelect");
    if (gridSizeSelect) {
      gridSizeSelect.onchange = () => {
        this.send({ action: "reset", config: this.gatherConfigFromUI() });
      };
    }

    // Maze selector
    const mazeSelect = document.getElementById("mazeSelect");
    if (mazeSelect) {
      mazeSelect.onchange = () => {
        this.send({ action: "reset", config: this.gatherConfigFromUI() });
      };
    }

    // Randomize seed
    const btnRandomSeed = document.getElementById("btnRandomSeed");
    if (btnRandomSeed) {
      btnRandomSeed.onclick = () => {
        const newSeed = Math.floor(Math.random() * 90000) + 10000;
        const seedInput = document.getElementById("seedInput");
        if (seedInput) seedInput.value = newSeed;
        this.send({ action: "reset", config: this.gatherConfigFromUI() });
      };
    }

    // Sound toggle
    const btnMute = document.getElementById("btnMute");
    if (btnMute) {
      btnMute.onclick = () => {
        const isMuted = this.audio.toggleMute();
        btnMute.textContent = isMuted ? "🔇 SOUND OFF" : "🔊 SOUND ON";
        btnMute.classList.toggle("active", !isMuted);
      };
    }

    // Terminal filters
    document.querySelectorAll(".pill-btn").forEach(btn => {
      btn.onclick = () => {
        document.querySelectorAll(".pill-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        this.terminal.setFilter(btn.dataset.filter);
      };
    });

    // Terminal search
    const termSearch = document.getElementById("termSearch");
    if (termSearch) {
      termSearch.oninput = (e) => this.terminal.setSearchQuery(e.target.value);
    }

    // Auto-scroll toggle
    const chkAutoScroll = document.getElementById("chkAutoScroll");
    if (chkAutoScroll) {
      chkAutoScroll.onchange = (e) => this.terminal.setAutoScroll(e.target.checked);
    }

    // Export logs buttons
    const btnExportJson = document.getElementById("btnExportJson");
    if (btnExportJson) btnExportJson.onclick = () => this.terminal.exportLogsJson();
    const btnExportCsv = document.getElementById("btnExportCsv");
    if (btnExportCsv) btnExportCsv.onclick = () => this.terminal.exportLogsCsv();

    // Hacker CLI Input
    const cliInput = document.getElementById("cliInput");
    if (cliInput) {
      cliInput.onkeydown = (e) => {
        if (e.key === "Enter") {
          const cmd = cliInput.value.trim();
          cliInput.value = "";
          this.executeCliCommand(cmd);
        }
      };
    }
  }

  syncGameModeUI() {
    const isSnake = this.gameMode === "snake";
    const tabSnake = document.getElementById("tabSnake");
    const tabTetris = document.getElementById("tabTetris");
    if (tabSnake && tabTetris) {
      tabSnake.classList.toggle("active", isSnake);
      tabTetris.classList.toggle("active", !isSnake);
    }

    const icon = document.getElementById("arenaIcon");
    const title = document.getElementById("arenaTitle");
    if (icon) icon.textContent = isSnake ? "🐍" : "🧱";
    if (title) title.textContent = isSnake ? "Cyber-Snake AI Arena // Research Lab" : "Cyber-Tetris AI Arena // Research Lab";

    // Show/hide snake specific controls
    document.querySelectorAll(".snake-opt").forEach(el => {
      el.style.display = isSnake ? "flex" : "none";
    });

    // Update table header metrics
    const thPrimary = document.getElementById("thPrimaryMetric");
    const thSecondary = document.getElementById("thSecondaryMetric");
    if (thPrimary) thPrimary.textContent = isSnake ? "Score (Apples)" : "Lines Cleared";
    if (thSecondary) thSecondary.textContent = isSnake ? "Steps Survived" : "Pieces Placed";

    const chartTitle = document.getElementById("chartMetricTitle");
    if (chartTitle) chartTitle.textContent = isSnake ? "🍎 Cumulative Apples Eaten" : "🧱 Cumulative Lines Cleared";
  }

  executeCliCommand(rawCmd) {
    if (!rawCmd) return;
    const parts = rawCmd.split(" ");
    const action = parts[0].toLowerCase();

    if (action === "help") {
      this.terminal.addEvent({
        name: "SYSTEM",
        model_id: "system",
        color: "#00f3ff",
        turn: this.turn,
        decision: {
          direction: "CLI",
          confidence: 1.0,
          latency_ms: 0,
          is_safe: true,
          reasoning: "Commands: play, pause, step, reset, game tetris, game snake, seed <num>, export, clear"
        }
      });
    } else if (action === "play") {
      this.send({ action: "play" });
    } else if (action === "pause") {
      this.send({ action: "pause" });
    } else if (action === "step") {
      this.send({ action: "step" });
    } else if (action === "reset") {
      this.send({ action: "reset", config: this.gatherConfigFromUI() });
    } else if (action === "clear") {
      this.terminal.clear();
    } else if (action === "game" && parts[1]) {
      const g = parts[1].toLowerCase();
      if (g === "tetris" || g === "snake") {
        this.gameMode = g;
        this.send({ action: "switch_game", game_type: g });
      }
    } else if (action === "export") {
      this.terminal.exportLogsJson();
    }
  }

  gatherConfigFromUI() {
    const isSnake = this.gameMode === "snake";
    const gridSize = parseInt(document.getElementById("gridSizeSelect")?.value || "8");
    const mazeType = document.getElementById("mazeSelect")?.value || "open";
    const seed = parseInt(document.getElementById("seedInput")?.value || "42");
    const stepDelay = parseInt(document.getElementById("speedSlider")?.value || "300");

    return {
      game_mode: this.gameMode,
      width: isSnake ? gridSize : 10,
      height: isSnake ? gridSize : 20,
      maze_type: mazeType,
      seed: seed,
      step_delay_ms: stepDelay,
    };
  }

  updateHeaderStats() {
    const turnEl = document.getElementById("displayTurn");
    if (turnEl) turnEl.textContent = String(this.turn);
    const seedEl = document.getElementById("displaySeed");
    if (seedEl) seedEl.textContent = String(this.config.seed || 42);
  }

  updatePlayPauseButton() {
    const btnPlay = document.getElementById("btnPlay");
    if (!btnPlay) return;

    if (this.isRunning) {
      btnPlay.innerHTML = `<span class="icon">⏸</span> PAUSE`;
      btnPlay.classList.add("active");
    } else {
      btnPlay.innerHTML = `<span class="icon">▶</span> RUN ARENA`;
      btnPlay.classList.remove("active");
    }
  }

  renderViewports() {
    const container = document.getElementById("viewportsGrid");
    if (!container) return;

    container.innerHTML = "";
    this.renderers = {};

    const isSnake = this.gameMode === "snake";

    this.models.forEach(model => {
      const card = document.createElement("div");
      card.className = "viewport-card";
      card.id = `card-${this._sanitizeId(model.model_id)}`;

      const shortType = model.model_type.toUpperCase();
      const badgeColor = model.color || "#00f3ff";

      card.innerHTML = `
        <div class="card-top">
          <div class="card-model-info">
            <span class="model-dot" style="background:${badgeColor}; box-shadow:0 0 8px ${badgeColor}"></span>
            <span class="card-model-title">${model.name}</span>
            <span class="card-model-type">${shortType}</span>
          </div>
          <span class="card-latency-badge" id="lat-${this._sanitizeId(model.model_id)}" style="color:${badgeColor}">
            -- ms
          </span>
        </div>

        <div class="canvas-container" style="aspect-ratio:${isSnake ? '1 / 1' : '10 / 18'}">
          <canvas class="game-canvas" id="canvas-${this._sanitizeId(model.model_id)}"></canvas>
          <span class="canvas-overlay-state" id="overlay-${this._sanitizeId(model.model_id)}" style="display:none"></span>
        </div>

        <div class="card-stats-row">
          <div class="stat-box">
            <span class="stat-label">${isSnake ? 'SCORE' : 'LINES'}</span>
            <span class="stat-value" id="score-${this._sanitizeId(model.model_id)}">0</span>
          </div>
          <div class="stat-box">
            <span class="stat-label">${isSnake ? 'STEPS' : 'PIECES'}</span>
            <span class="stat-value" id="steps-${this._sanitizeId(model.model_id)}">0</span>
          </div>
          <div class="stat-box">
            <span class="stat-label">CONFIDENCE</span>
            <span class="stat-value" id="conf-${this._sanitizeId(model.model_id)}">--%</span>
          </div>
        </div>

        <div class="card-reasoning-footer" id="reason-${this._sanitizeId(model.model_id)}">
          Awaiting arena start...
        </div>
      `;

      card.onclick = () => {
        this.inspector.show(model, this.lastEvents[model.model_id]);
      };

      container.appendChild(card);

      const canvas = card.querySelector(".game-canvas");
      let renderer;
      if (isSnake) {
        renderer = new SnakeCanvasRenderer(canvas);
      } else {
        renderer = new TetrisCanvasRenderer(canvas);
      }
      renderer.resize();
      renderer.render(model.game_state || {}, model.color);
      this.renderers[model.model_id] = renderer;
    });

    window.addEventListener("resize", () => {
      Object.values(this.renderers).forEach(r => r.resize());
    });
  }

  updateCardHUD(modelId, gameState, telemetry, decision) {
    const sId = this._sanitizeId(modelId);

    const latEl = document.getElementById(`lat-${sId}`);
    if (latEl && decision?.latency_ms !== undefined) {
      latEl.textContent = `${decision.latency_ms}ms`;
    }

    const scoreEl = document.getElementById(`score-${sId}`);
    if (scoreEl && gameState) {
      const val = this.gameMode === "snake" ? (gameState.score || 0) : (gameState.lines_cleared || 0);
      scoreEl.textContent = String(val);
    }

    const stepsEl = document.getElementById(`steps-${sId}`);
    if (stepsEl && gameState) {
      const val = this.gameMode === "snake" ? (gameState.steps || 0) : (gameState.pieces_placed || 0);
      stepsEl.textContent = String(val);
    }

    const confEl = document.getElementById(`conf-${sId}`);
    if (confEl && decision?.confidence !== undefined) {
      confEl.textContent = `${Math.round(decision.confidence * 100)}%`;
    }

    const reasonEl = document.getElementById(`reason-${sId}`);
    if (reasonEl && decision?.reasoning) {
      reasonEl.textContent = decision.reasoning;
    }

    const overlayEl = document.getElementById(`overlay-${sId}`);
    if (overlayEl) {
      if (gameState && !gameState.is_alive) {
        overlayEl.style.display = "block";
        overlayEl.style.background = "rgba(239, 68, 68, 0.85)";
        overlayEl.style.color = "#fff";
        overlayEl.textContent = `DEAD: ${(gameState.death_reason || 'LOCKOUT').replace('_', ' ').toUpperCase()}`;
      } else {
        overlayEl.style.display = "none";
      }
    }
  }

  updateLeaderboard() {
    const tbody = document.getElementById("leaderboardBody");
    if (!tbody) return;

    const isSnake = this.gameMode === "snake";

    const sorted = [...this.models].sort((a, b) => {
      const scoreA = isSnake ? (a.game_state?.score || 0) : (a.game_state?.lines_cleared || 0);
      const scoreB = isSnake ? (b.game_state?.score || 0) : (b.game_state?.lines_cleared || 0);
      if (scoreB !== scoreA) return scoreB - scoreA;

      const stepsA = isSnake ? (a.game_state?.steps || 0) : (a.game_state?.pieces_placed || 0);
      const stepsB = isSnake ? (b.game_state?.steps || 0) : (b.game_state?.pieces_placed || 0);
      if (stepsB !== stepsA) return stepsB - stepsA;

      const latA = a.telemetry?.avg_latency_ms || 9999;
      const latB = b.telemetry?.avg_latency_ms || 9999;
      return latA - latB;
    });

    tbody.innerHTML = sorted.map((m, idx) => {
      const rank = idx === 0 ? "🥇" : (idx === 1 ? "🥈" : (idx === 2 ? "🥉" : `#${idx + 1}`));
      const isAlive = m.game_state?.is_alive !== false;
      const statusClass = isAlive ? "alive" : "crashed";
      const statusText = isAlive ? "ALIVE" : (m.game_state?.death_reason || "DEAD").replace("_", " ").toUpperCase();
      const avgLat = m.telemetry?.avg_latency_ms || 0;
      const latClass = avgLat < 120 ? "metric-fast" : (avgLat > 1500 ? "metric-slow" : "metric-highlight");
      const cost = m.telemetry?.total_cost_usd > 0 ? `$${m.telemetry.total_cost_usd.toFixed(6)}` : "$0.00";

      const primaryVal = isSnake ? (m.game_state?.score || 0) : `${m.game_state?.lines_cleared || 0} lines (${m.game_state?.score || 0} pts)`;
      const secondaryVal = isSnake ? (m.game_state?.steps || 0) : (m.game_state?.pieces_placed || 0);

      return `
        <tr onclick="window.app.inspector.show(window.app.modelsMap['${m.model_id}'], window.app.lastEvents['${m.model_id}'])" style="cursor:pointer">
          <td style="font-weight:bold">${rank}</td>
          <td>
            <div class="model-name-cell">
              <span class="model-dot" style="background:${m.color || '#00f3ff'}"></span>
              <span>${m.name}</span>
            </div>
          </td>
          <td><span class="status-tag ${statusClass}">${statusText}</span></td>
          <td class="metric-highlight">${primaryVal}</td>
          <td>${secondaryVal}</td>
          <td class="${latClass}">${avgLat}ms</td>
          <td>${m.telemetry?.p99_latency_ms || 0}ms</td>
          <td>${cost}</td>
        </tr>
      `;
    }).join("");
  }

  _sanitizeId(str) {
    return (str || "").replace(/[^a-zA-Z0-9_-]/g, "_");
  }
}

window.addEventListener("DOMContentLoaded", () => {
  window.app = new ArenaApp();
});
