import React, { useRef, useEffect, useState } from 'react';

const TETRIS_COLORS = {
  I: '#00f0ff',
  O: '#facc15',
  T: '#a855f7',
  S: '#22c55e',
  Z: '#ef4444',
  J: '#3b82f6',
  L: '#f97316',
};

const TETROMINO_SHAPES = {
  I: [
    [[0, 1], [1, 1], [2, 1], [3, 1]],
    [[2, 0], [2, 1], [2, 2], [2, 3]],
    [[0, 2], [1, 2], [2, 2], [3, 2]],
    [[1, 0], [1, 1], [1, 2], [1, 3]],
  ],
  O: [
    [[1, 0], [2, 0], [1, 1], [2, 1]],
    [[1, 0], [2, 0], [1, 1], [2, 1]],
    [[1, 0], [2, 0], [1, 1], [2, 1]],
    [[1, 0], [2, 0], [1, 1], [2, 1]],
  ],
  T: [
    [[1, 0], [0, 1], [1, 1], [2, 1]],
    [[1, 0], [1, 1], [2, 1], [1, 2]],
    [[0, 1], [1, 1], [2, 1], [1, 2]],
    [[1, 0], [0, 1], [1, 1], [1, 2]],
  ],
  S: [
    [[1, 0], [2, 0], [0, 1], [1, 1]],
    [[1, 0], [1, 1], [2, 1], [2, 2]],
    [[1, 1], [2, 1], [0, 2], [1, 2]],
    [[0, 0], [0, 1], [1, 1], [1, 2]],
  ],
  Z: [
    [[0, 0], [1, 0], [1, 1], [2, 1]],
    [[2, 0], [1, 1], [2, 1], [1, 2]],
    [[0, 1], [1, 1], [1, 2], [2, 2]],
    [[1, 0], [0, 1], [1, 1], [0, 2]],
  ],
  J: [
    [[0, 0], [0, 1], [1, 1], [2, 1]],
    [[1, 0], [2, 0], [1, 1], [1, 2]],
    [[0, 1], [1, 1], [2, 1], [2, 2]],
    [[1, 0], [1, 1], [0, 2], [1, 2]],
  ],
  L: [
    [[2, 0], [0, 1], [1, 1], [2, 1]],
    [[1, 0], [1, 1], [1, 2], [2, 2]],
    [[0, 1], [1, 1], [2, 1], [0, 2]],
    [[0, 0], [1, 0], [1, 1], [1, 2]],
  ],
};

export default function TetrisCanvas({
  gameState,
  decision,
  preGrid,
  modelColor = '#00f3ff',
  isAlive = true,
  speedDelayMs = 300,
}) {
  const canvasRef = useRef(null);
  const animRef = useRef({
    active: false,
    piece: null,
    coords: null,
    col: 0,
    targetY: 18,
    startTime: 0,
    duration: 250,
  });

  const [activeCommandText, setActiveCommandText] = useState('READY');

  // Trigger real-time falling animation whenever a new piece decision arrives
  useEffect(() => {
    if (!decision || !decision.piece) return;

    const pieceType = decision.piece;
    const rot = decision.rotation || 0;
    const col = decision.column || 0;
    const targetY = decision.drop_y !== undefined ? decision.drop_y : 18;

    const shapes = TETROMINO_SHAPES[pieceType] || TETROMINO_SHAPES['I'];
    const coords = shapes[rot % shapes.length];

    // Falling animation duration scaled with speed slider (between 120ms and 450ms)
    const duration = Math.max(120, Math.min(450, speedDelayMs * 0.75));

    animRef.current = {
      active: true,
      piece: pieceType,
      coords: coords,
      col: col,
      targetY: targetY,
      startTime: performance.now(),
      duration: duration,
      commands: decision.commands || [
        `SPAWN ${pieceType}`,
        `ROTATE ${rot * 90}°`,
        `SHIFT COL ${col}`,
        `DROP Y:${targetY}`,
      ],
    };
  }, [decision, speedDelayMs]);

  // Main 60fps render loop
  useEffect(() => {
    let reqId;

    const render = (time) => {
      const canvas = canvasRef.current;
      if (!canvas) return;
      const ctx = canvas.getContext('2d');

      const rect = canvas.getBoundingClientRect();
      const dpr = window.devicePixelRatio || 1;
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      ctx.scale(dpr, dpr);

      const width = rect.width;
      const height = rect.height;

      const gridW = gameState?.width || 10;
      const gridH = gameState?.height || 20;
      const cellW = width / gridW;
      const cellH = height / gridH;

      // Clear background
      ctx.fillStyle = '#03060b';
      ctx.fillRect(0, 0, width, height);

      // Subtle grid
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.04)';
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

      // Check falling animation state
      const anim = animRef.current;
      let isFalling = false;
      let currentDropY = 0;
      let activeCmd = 'STANDBY';

      if (anim.active && isAlive) {
        const elapsed = time - anim.startTime;
        const progress = Math.min(1, elapsed / anim.duration);

        // Calculate current falling Y (smooth cubic ease-in for realistic gravity drop)
        currentDropY = (progress * progress) * anim.targetY;

        // Command progression
        if (progress < 0.25) activeCmd = anim.commands[0] || 'SPAWN';
        else if (progress < 0.50) activeCmd = anim.commands[1] || 'ROTATE';
        else if (progress < 0.75) activeCmd = anim.commands[2] || 'SHIFT COL';
        else activeCmd = anim.commands[3] || 'HARD DROP';

        if (progress >= 1) {
          anim.active = false;
          activeCmd = 'LOCKED';
        } else {
          isFalling = true;
        }
      }

      setActiveCommandText(activeCmd);

      // Which grid to draw: draw preGrid during fall, or current locked grid once landed
      const gridToDraw = (isFalling && preGrid) ? preGrid : (gameState?.grid || []);

      // Draw Locked / Placed Grid Blocks
      for (let y = 0; y < gridH; y++) {
        for (let x = 0; x < gridW; x++) {
          const piece = gridToDraw[y]?.[x];
          if (piece) {
            const px = x * cellW;
            const py = y * cellH;
            const pColor = TETRIS_COLORS[piece] || modelColor;

            ctx.fillStyle = isAlive ? pColor : '#64748b';
            ctx.shadowColor = isAlive ? pColor : 'transparent';
            ctx.shadowBlur = 4;
            ctx.beginPath();
            ctx.roundRect(px + 1.5, py + 1.5, cellW - 3, cellH - 3, 2.5);
            ctx.fill();
            ctx.shadowBlur = 0;

            // Highlight border
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.35)';
            ctx.lineWidth = 1;
            ctx.stroke();
          }
        }
      }

      // REAL-TIME FALLING BRICK & GHOST PIECE RENDERING
      if (isFalling && anim.coords) {
        const pColor = TETRIS_COLORS[anim.piece] || modelColor;

        // 1. Draw Ghost Piece (Shadow at landing targetY)
        ctx.strokeStyle = pColor;
        ctx.lineWidth = 1.5;
        ctx.setLineDash([3, 3]);
        ctx.fillStyle = `${pColor}22`;

        for (const [px, py] of anim.coords) {
          const gx = (px + anim.col) * cellW;
          const gy = (py + anim.targetY) * cellH;
          if (gy < height) {
            ctx.beginPath();
            ctx.roundRect(gx + 1.5, gy + 1.5, cellW - 3, cellH - 3, 2.5);
            ctx.fill();
            ctx.stroke();
          }
        }
        ctx.setLineDash([]); // Reset line dash

        // 2. Draw Active Falling Piece at currentDropY
        ctx.fillStyle = pColor;
        ctx.shadowColor = pColor;
        ctx.shadowBlur = 12;

        for (const [px, py] of anim.coords) {
          const gx = (px + anim.col) * cellW;
          const gy = (py + currentDropY) * cellH;

          if (gy < height) {
            ctx.beginPath();
            ctx.roundRect(gx + 1.5, gy + 1.5, cellW - 3, cellH - 3, 2.5);
            ctx.fill();

            // Inner gloss highlight
            ctx.strokeStyle = '#fff';
            ctx.lineWidth = 1.2;
            ctx.stroke();
          }
        }
        ctx.shadowBlur = 0;
      }

      // Next Piece HUD Box in Top-Right
      if (gameState?.next_piece) {
        const nextP = gameState.next_piece;
        const nextColor = TETRIS_COLORS[nextP] || '#fff';

        ctx.fillStyle = 'rgba(10, 15, 26, 0.85)';
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
        ctx.lineWidth = 1;
        const hudW = cellW * 3.5;
        const hudH = cellH * 2.2;
        ctx.roundRect(width - hudW - 4, 4, hudW, hudH, 4);
        ctx.fill();
        ctx.stroke();

        ctx.fillStyle = nextColor;
        ctx.font = 'bold 9px monospace';
        ctx.fillText(`NEXT: ${nextP}`, width - hudW + 4, 16);
      }

      // Death / Stack Out Overlay
      if (!isAlive) {
        ctx.fillStyle = 'rgba(239, 68, 68, 0.35)';
        ctx.fillRect(0, 0, width, height);

        ctx.strokeStyle = '#ef4444';
        ctx.lineWidth = 3;
        ctx.strokeRect(4, 4, width - 8, height - 8);

        ctx.fillStyle = '#fff';
        ctx.font = 'bold 14px monospace';
        ctx.textAlign = 'center';
        ctx.fillText('STACK OUT', width / 2, height / 2);
        ctx.textAlign = 'left';
      }

      reqId = requestAnimationFrame(render);
    };

    reqId = requestAnimationFrame(render);
    return () => cancelAnimationFrame(reqId);
  }, [gameState, preGrid, modelColor, isAlive]);

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      <canvas
        ref={canvasRef}
        style={{ width: '100%', height: '100%', display: 'block' }}
      />
      {/* Live Command Overlay Chip */}
      <div style={{
        position: 'absolute',
        top: '6px',
        left: '6px',
        background: 'rgba(0, 0, 0, 0.75)',
        border: '1px solid rgba(0, 243, 255, 0.4)',
        borderRadius: '4px',
        padding: '2px 6px',
        fontFamily: 'var(--font-mono)',
        fontSize: '0.68rem',
        fontWeight: 700,
        color: 'var(--cyan-glow)',
        pointerEvents: 'none',
        display: 'flex',
        alignItems: 'center',
        gap: '4px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.6)'
      }}>
        <span style={{ color: '#10b981' }}>●</span>
        <span>{activeCommandText}</span>
      </div>
    </div>
  );
}
