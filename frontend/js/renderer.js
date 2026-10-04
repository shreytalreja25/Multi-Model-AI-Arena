/**
 * Canvas 2D Renderer for Snake AI Arena viewports.
 * Handles smooth 60fps interpolation, neon trails, food animation, obstacles, and crash forensics.
 */

class SnakeCanvasRenderer {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d");
    this.animationPhase = 0;
    this.particles = [];
  }

  resize() {
    const rect = this.canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    this.canvas.width = rect.width * dpr;
    this.canvas.height = rect.height * dpr;
    this.ctx.scale(dpr, dpr);
    this.displayWidth = rect.width;
    this.displayHeight = rect.height;
  }

  render(gameState, modelColor = "#00f3ff", isAlive = true, deathReason = null) {
    if (!this.displayWidth) this.resize();

    const ctx = this.ctx;
    const width = this.displayWidth;
    const height = this.displayHeight;

    const gridW = gameState.width || 8;
    const gridH = gameState.height || 8;
    const cellW = width / gridW;
    const cellH = height / gridH;

    // Clear background
    ctx.fillStyle = "#03060b";
    ctx.fillRect(0, 0, width, height);

    // Draw subtle grid lines / points
    ctx.strokeStyle = "rgba(255, 255, 255, 0.04)";
    ctx.lineWidth = 1;
    for (let x = 0; x <= gridW; x++) {
      ctx.beginPath();
      ctx.moveTo(x * cellW, 0);
      ctx.lineTo(x * cellW, height);
      ctx.stroke();
    }
    for (let y = 0; y <= gridH; y++) {
      ctx.beginPath();
      ctx.moveTo(0, y * cellH);
      ctx.lineTo(width, y * cellH);
      ctx.stroke();
    }

    // Draw Obstacles
    if (gameState.obstacles) {
      ctx.fillStyle = "rgba(239, 68, 68, 0.25)";
      ctx.strokeStyle = "rgba(239, 68, 68, 0.6)";
      ctx.lineWidth = 1.5;

      for (const [ox, oy] of gameState.obstacles) {
        const px = ox * cellW;
        const py = oy * cellH;
        ctx.fillRect(px + 2, py + 2, cellW - 4, cellH - 4);
        ctx.strokeRect(px + 2, py + 2, cellW - 4, cellH - 4);

        // Hazard diagonals inside obstacle
        ctx.beginPath();
        ctx.moveTo(px + 4, py + 4);
        ctx.lineTo(px + cellW - 4, py + cellH - 4);
        ctx.stroke();
      }
    }

    // Draw Food with pulsating aura
    if (gameState.food && gameState.food[0] >= 0) {
      const [fx, fy] = gameState.food;
      const fcx = fx * cellW + cellW / 2;
      const fcy = fy * cellH + cellH / 2;
      const radius = Math.min(cellW, cellH) * 0.32;

      this.animationPhase = (this.animationPhase + 0.08) % (Math.PI * 2);
      const pulse = 1 + Math.sin(this.animationPhase) * 0.15;

      // Outer glow
      const grad = ctx.createRadialGradient(fcx, fcy, 2, fcx, fcy, radius * 2.2 * pulse);
      grad.addColorStop(0, "rgba(244, 63, 94, 0.8)");
      grad.addColorStop(0.5, "rgba(244, 63, 94, 0.3)");
      grad.addColorStop(1, "rgba(244, 63, 94, 0)");

      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.arc(fcx, fcy, radius * 2.2 * pulse, 0, Math.PI * 2);
      ctx.fill();

      // Food core
      ctx.fillStyle = "#ff0055";
      ctx.beginPath();
      ctx.arc(fcx, fcy, radius, 0, Math.PI * 2);
      ctx.fill();

      ctx.fillStyle = "#fff";
      ctx.beginPath();
      ctx.arc(fcx - radius * 0.3, fcy - radius * 0.3, radius * 0.28, 0, Math.PI * 2);
      ctx.fill();
    }

    // Draw Snake Body
    if (gameState.body && gameState.body.length > 0) {
      const body = gameState.body;
      const len = body.length;

      for (let i = len - 1; i >= 0; i--) {
        const [bx, by] = body[i];
        const px = bx * cellW + 2;
        const py = by * cellH + 2;
        const bw = cellW - 4;
        const bh = cellH - 4;
        const isHead = i === 0;

        if (isHead) {
          // Snake Head with strong glow
          ctx.shadowColor = modelColor;
          ctx.shadowBlur = isAlive ? 14 : 0;
          ctx.fillStyle = isAlive ? modelColor : "#ef4444";
          ctx.beginPath();
          ctx.roundRect(px, py, bw, bh, Math.min(bw, bh) * 0.3);
          ctx.fill();
          ctx.shadowBlur = 0;

          // Eye indicators
          ctx.fillStyle = "#000";
          const eyeSize = Math.min(cellW, cellH) * 0.14;
          const dir = gameState.direction || "RIGHT";
          let e1x = px + bw * 0.3, e1y = py + bh * 0.3;
          let e2x = px + bw * 0.7, e2y = py + bh * 0.3;

          if (dir === "RIGHT") {
            e1x = px + bw * 0.7; e1y = py + bh * 0.3;
            e2x = px + bw * 0.7; e2y = py + bh * 0.7;
          } else if (dir === "LEFT") {
            e1x = px + bw * 0.3; e1y = py + bh * 0.3;
            e2x = px + bw * 0.3; e2y = py + bh * 0.7;
          } else if (dir === "DOWN") {
            e1x = px + bw * 0.3; e1y = py + bh * 0.7;
            e2x = px + bw * 0.7; e2y = py + bh * 0.7;
          }

          ctx.beginPath();
          ctx.arc(e1x, e1y, eyeSize, 0, Math.PI * 2);
          ctx.arc(e2x, e2y, eyeSize, 0, Math.PI * 2);
          ctx.fill();

        } else {
          // Body segments with fading gradient
          const alpha = 0.35 + (0.65 * (1 - i / len));
          ctx.fillStyle = this._hexToRgba(isAlive ? modelColor : "#64748b", alpha);
          ctx.beginPath();
          ctx.roundRect(px + 1, py + 1, bw - 2, bh - 2, Math.min(bw, bh) * 0.2);
          ctx.fill();
        }
      }
    }

    // Crash Visual Overlay
    if (!isAlive && gameState.head) {
      const [hx, hy] = gameState.head;
      const hcx = hx * cellW + cellW / 2;
      const hcy = hy * cellH + cellH / 2;

      ctx.strokeStyle = "#ef4444";
      ctx.lineWidth = 2.5;
      const crossSize = Math.min(cellW, cellH) * 0.6;

      ctx.beginPath();
      ctx.moveTo(hcx - crossSize, hcy - crossSize);
      ctx.lineTo(hcx + crossSize, hcy + crossSize);
      ctx.moveTo(hcx + crossSize, hcy - crossSize);
      ctx.lineTo(hcx - crossSize, hcy + crossSize);
      ctx.stroke();
    }
  }

  _hexToRgba(hex, alpha) {
    if (hex.startsWith("#")) {
      const c = hex.slice(1);
      const r = parseInt(c.slice(0, 2), 16);
      const g = parseInt(c.slice(2, 4), 16);
      const b = parseInt(c.slice(4, 6), 16);
      return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }
    return hex;
  }
}
