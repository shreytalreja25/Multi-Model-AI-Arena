import React, { useRef, useEffect } from 'react';

const PIECE_GLYPHS = {
  // White pieces
  'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',
  // Black pieces
  'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟',
};

export default function ChessCanvas({
  gameState,
  lastEvent,
  modelColor = '#00f0ff',
  width = 300,
  height = 300,
}) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const dpr = window.devicePixelRatio || 1;

    canvas.width = width * dpr;
    canvas.height = height * dpr;
    ctx.scale(dpr, dpr);

    // Padding for coordinates
    const pad = 18;
    const boardSize = Math.min(width, height) - pad * 2;
    const tileSize = boardSize / 8;
    const offsetX = (width - boardSize) / 2 + 6;
    const offsetY = (height - boardSize) / 2 - 6;

    // Background
    ctx.fillStyle = '#070a12';
    ctx.fillRect(0, 0, width, height);

    // Subtle background grid glow
    const grad = ctx.createRadialGradient(width / 2, height / 2, 20, width / 2, height / 2, width);
    grad.addColorStop(0, 'rgba(0, 240, 255, 0.05)');
    grad.addColorStop(1, 'rgba(0, 0, 0, 0.6)');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, width, height);

    const lastMove = gameState?.last_move;
    const board2d = gameState?.board_2d || [];
    const isCheck = gameState?.is_check || false;

    // Draw 8x8 Board Tiles
    for (let r = 0; r < 8; r++) {
      for (let c = 0; c < 8; c++) {
        const x = offsetX + c * tileSize;
        const y = offsetY + r * tileSize;
        const isLight = (r + c) % 2 === 0;

        ctx.fillStyle = isLight ? '#162235' : '#0c1320';
        ctx.fillRect(x, y, tileSize, tileSize);

        // Subtle tile borders
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.04)';
        ctx.lineWidth = 1;
        ctx.strokeRect(x, y, tileSize, tileSize);

        // Highlight last move from/to squares
        const fileChar = String.fromCharCode(97 + c);
        const rankNum = 8 - r;
        const sqName = `${fileChar}${rankNum}`;

        if (lastMove && (lastMove.from === sqName || lastMove.to === sqName)) {
          ctx.fillStyle = lastMove.to === sqName ? 'rgba(0, 240, 255, 0.28)' : 'rgba(168, 85, 247, 0.20)';
          ctx.fillRect(x, y, tileSize, tileSize);

          ctx.strokeStyle = lastMove.to === sqName ? modelColor : '#a855f7';
          ctx.lineWidth = 2;
          ctx.strokeRect(x + 1, y + 1, tileSize - 2, tileSize - 2);
        }
      }
    }

    // Outer board cyber border
    ctx.strokeStyle = 'rgba(0, 240, 255, 0.35)';
    ctx.lineWidth = 2;
    ctx.strokeRect(offsetX, offsetY, boardSize, boardSize);

    // Draw Files (a-h) along bottom
    ctx.font = '10px "Fira Code", monospace';
    ctx.fillStyle = 'rgba(0, 240, 255, 0.6)';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';
    for (let c = 0; c < 8; c++) {
      const fileChar = String.fromCharCode(97 + c);
      const x = offsetX + c * tileSize + tileSize / 2;
      ctx.fillText(fileChar, x, offsetY + boardSize + 4);
    }

    // Draw Ranks (1-8) along left
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';
    for (let r = 0; r < 8; r++) {
      const rankNum = 8 - r;
      const y = offsetY + r * tileSize + tileSize / 2;
      ctx.fillText(String(rankNum), offsetX - 5, y);
    }

    // Draw Pieces
    const pieceFontSize = Math.floor(tileSize * 0.78);
    ctx.font = `${pieceFontSize}px "Segoe UI Symbol", "Apple Color Emoji", "Noto Color Emoji", sans-serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';

    for (let r = 0; r < 8; r++) {
      const row = board2d[r] || [];
      for (let c = 0; c < 8; c++) {
        const item = row[c];
        if (!item) continue;

        const x = offsetX + c * tileSize + tileSize / 2;
        const y = offsetY + r * tileSize + tileSize / 2 + 1;
        const sym = item.symbol;
        const glyph = PIECE_GLYPHS[sym] || sym;
        const isWhite = item.color === 'w';

        // Red alert if King in check
        if (isCheck && item.type === 'k' && isWhite) {
          ctx.fillStyle = 'rgba(255, 0, 85, 0.4)';
          ctx.beginPath();
          ctx.arc(x, y, tileSize * 0.42, 0, Math.PI * 2);
          ctx.fill();
        }

        // Shadow & glow
        ctx.shadowColor = isWhite ? 'rgba(0, 240, 255, 0.8)' : 'rgba(255, 42, 109, 0.8)';
        ctx.shadowBlur = isWhite ? 8 : 10;

        ctx.fillStyle = isWhite ? '#ffffff' : '#ff2a6d';
        ctx.fillText(glyph, x, y);

        // Reset shadow
        ctx.shadowBlur = 0;
      }
    }

    // Overlay Game Over Banner if terminated
    if (gameState && !gameState.is_alive) {
      ctx.fillStyle = 'rgba(0, 0, 0, 0.75)';
      ctx.fillRect(offsetX, offsetY, boardSize, boardSize);

      ctx.fillStyle = '#ff0055';
      ctx.font = 'bold 15px "Orbitron", sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('CHECKMATE / DRAW', offsetX + boardSize / 2, offsetY + boardSize / 2 - 8);

      ctx.fillStyle = '#00f0ff';
      ctx.font = '11px "Fira Code", monospace';
      ctx.fillText(`RESULT: ${gameState.result || '*'}`, offsetX + boardSize / 2, offsetY + boardSize / 2 + 14);
    }

  }, [gameState, lastEvent, modelColor, width, height]);

  const matDiff = gameState?.material_diff || 0;
  const isCheck = gameState?.is_check;
  const lastDec = lastEvent?.decision;

  return (
    <div style={{ position: 'relative', width, height, margin: '0 auto' }}>
      <canvas
        ref={canvasRef}
        style={{
          width,
          height,
          display: 'block',
          borderRadius: '8px',
          boxShadow: 'inset 0 0 20px rgba(0, 240, 255, 0.08)'
        }}
      />

      {/* Top HUD: Material & Check Badges */}
      <div style={{
        position: 'absolute',
        top: '6px',
        left: '10px',
        right: '10px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        pointerEvents: 'none'
      }}>
        <span style={{
          fontSize: '0.68rem',
          fontFamily: 'var(--font-mono)',
          padding: '2px 8px',
          borderRadius: '4px',
          background: 'rgba(0,0,0,0.7)',
          border: '1px solid rgba(255,255,255,0.15)',
          color: matDiff > 0 ? '#34d399' : matDiff < 0 ? '#f87171' : 'var(--text-muted)'
        }}>
          {matDiff > 0 ? `+${matDiff} MAT` : matDiff < 0 ? `${matDiff} MAT` : 'BALANCED'}
        </span>

        {isCheck && (
          <span style={{
            fontSize: '0.68rem',
            fontFamily: 'var(--font-mono)',
            fontWeight: 'bold',
            padding: '2px 8px',
            borderRadius: '4px',
            background: 'rgba(255, 0, 85, 0.25)',
            border: '1px solid #ff0055',
            color: '#ff0055',
            animation: 'pulseGlow 1s infinite'
          }}>
            ⚠️ CHECK
          </span>
        )}
      </div>

      {/* Bottom Move HUD */}
      {lastDec && (
        <div style={{
          position: 'absolute',
          bottom: '4px',
          left: '8px',
          right: '8px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '3px 8px',
          background: 'rgba(9, 13, 23, 0.85)',
          border: '1px solid rgba(0, 240, 255, 0.2)',
          borderRadius: '4px',
          fontSize: '0.70rem',
          fontFamily: 'var(--font-mono)',
          pointerEvents: 'none'
        }}>
          <span style={{ color: modelColor, fontWeight: 'bold' }}>
            {lastDec.san || lastDec.direction}
          </span>
          <span style={{ color: 'var(--text-muted)' }}>
            {lastDec.latency_ms ? `${lastDec.latency_ms}ms` : ''}
          </span>
        </div>
      )}
    </div>
  );
}
