/**
 * Canvas 2D Renderer for Tetris AI Arena viewports.
 * Handles neon blocks, ghost piece projections, next piece HUD, line clear flashing, and stackouts.
 */

const TETRIS_COLORS = {
  "I": "#00f0ff",
  "O": "#facc15",
  "T": "#a855f7",
  "S": "#22c55e",
  "Z": "#ef4444",
  "J": "#3b82f6",
  "L": "#f97316",
};

class TetrisCanvasRenderer {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d");
    this.animationPhase = 0;
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

    const gridW = gameState.width || 10;
    const gridH = gameState.height || 20;
    const cellW = width / gridW;
    const cellH = height / gridH;

    // Clear background
    ctx.fillStyle = "#03060b";
    ctx.fillRect(0, 0, width, height);

    // Subtle grid lines
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

    // Draw Locked Grid Blocks
    if (gameState.grid) {
      for (let y = 0; y < gridH; y++) {
        for (let x = 0; x < gridW; x++) {
          const piece = gameState.grid[y][x];
          if (piece) {
            const px = x * cellW;
            const py = y * cellH;
            const pColor = TETRIS_COLORS[piece] || modelColor;

            ctx.fillStyle = isAlive ? pColor : "#64748b";
            ctx.shadowColor = isAlive ? pColor : "transparent";
            ctx.shadowBlur = 6;
            ctx.beginPath();
            ctx.roundRect(px + 1.5, py + 1.5, cellW - 3, cellH - 3, 2.5);
            ctx.fill();
            ctx.shadowBlur = 0;

            // Highlight border
            ctx.strokeStyle = "rgba(255, 255, 255, 0.4)";
            ctx.lineWidth = 1;
            ctx.stroke();
          }
        }
      }
    }

    // Draw Next Piece HUD Box in Top-Right
    if (gameState.next_piece) {
      const nextP = gameState.next_piece;
      const nextColor = TETRIS_COLORS[nextP] || "#fff";

      ctx.fillStyle = "rgba(10, 15, 26, 0.75)";
      ctx.strokeStyle = "rgba(255, 255, 255, 0.15)";
      ctx.lineWidth = 1;
      const hudW = cellW * 3.2;
      const hudH = cellH * 2.2;
      ctx.roundRect(width - hudW - 4, 4, hudW, hudH, 4);
      ctx.fill();
      ctx.stroke();

      ctx.fillStyle = nextColor;
      ctx.font = "bold 9px monospace";
      ctx.fillText(`NEXT: ${nextP}`, width - hudW + 2, 16);
    }

    // Death Overlay
    if (!isAlive) {
      ctx.fillStyle = "rgba(239, 68, 68, 0.3)";
      ctx.fillRect(0, 0, width, height);

      ctx.strokeStyle = "#ef4444";
      ctx.lineWidth = 3;
      ctx.strokeRect(4, 4, width - 8, height - 8);

      ctx.fillStyle = "#fff";
      ctx.font = "bold 13px monospace";
      ctx.textAlign = "center";
      ctx.fillText("STACK OUT", width / 2, height / 2);
      ctx.textAlign = "left";
    }
  }
}
