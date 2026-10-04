/**
 * Real-time Scientific Telemetry Charts for Snake AI Arena (Zero dependency).
 * Renders high-performance Canvas charts for Latency Time-series, Score Comparison, and Calibration.
 */

class TelemetryCharts {
  constructor(latencyCanvas, scoreCanvas) {
    this.latencyCanvas = latencyCanvas;
    this.latencyCtx = latencyCanvas ? latencyCanvas.getContext("2d") : null;

    this.scoreCanvas = scoreCanvas;
    this.scoreCtx = scoreCanvas ? scoreCanvas.getContext("2d") : null;

    this.latencyHistory = {}; // model_id -> [latencies]
    this.maxDataPoints = 35;
  }

  recordStep(modelId, latencyMs) {
    if (!this.latencyHistory[modelId]) {
      this.latencyHistory[modelId] = [];
    }
    this.latencyHistory[modelId].push(latencyMs);
    if (this.latencyHistory[modelId].length > this.maxDataPoints) {
      this.latencyHistory[modelId].shift();
    }
  }

  clear() {
    this.latencyHistory = {};
    this.drawLatencyChart({});
    this.drawScoreChart([]);
  }

  drawLatencyChart(modelsMap) {
    if (!this.latencyCtx) return;
    const ctx = this.latencyCtx;
    const w = this.latencyCanvas.width;
    const h = this.latencyCanvas.height;

    ctx.clearRect(0, 0, w, h);
    ctx.fillStyle = "#04070d";
    ctx.fillRect(0, 0, w, h);

    // Grid lines
    ctx.strokeStyle = "rgba(255, 255, 255, 0.05)";
    ctx.lineWidth = 1;
    for (let y = 20; y < h - 20; y += 30) {
      ctx.beginPath();
      ctx.moveTo(35, y);
      ctx.lineTo(w - 10, y);
      ctx.stroke();
    }

    // Determine max latency scale (minimum 500ms, max capped)
    let maxLat = 500;
    for (const arr of Object.values(this.latencyHistory)) {
      for (const v of arr) {
        if (v > maxLat) maxLat = v;
      }
    }
    maxLat = Math.ceil(maxLat * 1.15);

    // Y Axis labels
    ctx.fillStyle = "#64748b";
    ctx.font = "10px monospace";
    ctx.fillText(`${maxLat}ms`, 2, 22);
    ctx.fillText(`${Math.round(maxLat / 2)}ms`, 2, h / 2);
    ctx.fillText("0ms", 2, h - 8);

    // Plot each model's latency series
    for (const [mId, lats] of Object.entries(this.latencyHistory)) {
      if (lats.length < 2) continue;
      const model = modelsMap[mId] || {};
      const color = model.color || "#00f3ff";

      ctx.strokeStyle = color;
      ctx.lineWidth = 2;
      ctx.beginPath();

      const stepX = (w - 55) / (this.maxDataPoints - 1);
      const startOffset = this.maxDataPoints - lats.length;

      for (let i = 0; i < lats.length; i++) {
        const x = 40 + (startOffset + i) * stepX;
        const normY = lats[i] / maxLat;
        const y = h - 20 - normY * (h - 40);

        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();

      // Draw end point glowing dot
      const lastX = 40 + (startOffset + lats.length - 1) * stepX;
      const lastY = h - 20 - (lats[lats.length - 1] / maxLat) * (h - 40);
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(lastX, lastY, 3.5, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  drawScoreChart(modelsList) {
    if (!this.scoreCtx || !modelsList || modelsList.length === 0) return;
    const ctx = this.scoreCtx;
    const w = this.scoreCanvas.width;
    const h = this.scoreCanvas.height;

    ctx.clearRect(0, 0, w, h);
    ctx.fillStyle = "#04070d";
    ctx.fillRect(0, 0, w, h);

    const barHeight = Math.min(24, (h - 20) / modelsList.length);
    let maxScore = 5;
    for (const m of modelsList) {
      if ((m.game_state?.score || 0) > maxScore) maxScore = m.game_state.score;
    }

    modelsList.forEach((m, idx) => {
      const y = 12 + idx * (barHeight + 6);
      const score = m.game_state?.score || 0;
      const barWidth = Math.max(4, (score / maxScore) * (w - 140));

      ctx.fillStyle = "#94a3b8";
      ctx.font = "11px monospace";
      const shortName = (m.name || m.model_id).slice(0, 10);
      ctx.fillText(shortName, 5, y + barHeight * 0.7);

      ctx.fillStyle = m.color || "#00f3ff";
      ctx.beginPath();
      ctx.roundRect(85, y, barWidth, barHeight, 3);
      ctx.fill();

      ctx.fillStyle = "#fff";
      ctx.font = "bold 10px monospace";
      ctx.fillText(`${score} pts`, 92 + barWidth, y + barHeight * 0.7);
    });
  }
}
