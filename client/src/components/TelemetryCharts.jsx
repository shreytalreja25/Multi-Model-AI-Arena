import React, { useRef, useEffect } from 'react';
import { Activity, BarChart3 } from 'lucide-react';

export default function TelemetryCharts({ gameMode, models, latencyHistory }) {
  const latencyCanvasRef = useRef(null);
  const scoreCanvasRef = useRef(null);
  const isSnake = gameMode === 'snake';

  // Draw Latency Multi-Line Chart
  useEffect(() => {
    const canvas = latencyCanvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const w = canvas.width;
    const h = canvas.height;

    ctx.clearRect(0, 0, w, h);
    ctx.fillStyle = '#04070d';
    ctx.fillRect(0, 0, w, h);

    // Grid lines
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
    ctx.lineWidth = 1;
    for (let y = 20; y < h - 20; y += 30) {
      ctx.beginPath();
      ctx.moveTo(35, y);
      ctx.lineTo(w - 10, y);
      ctx.stroke();
    }

    let maxLat = 500;
    for (const arr of Object.values(latencyHistory)) {
      for (const v of arr) {
        if (v > maxLat) maxLat = v;
      }
    }
    maxLat = Math.ceil(maxLat * 1.15);

    // Labels
    ctx.fillStyle = '#64748b';
    ctx.font = '10px monospace';
    ctx.fillText(`${maxLat}ms`, 2, 22);
    ctx.fillText(`${Math.round(maxLat / 2)}ms`, 2, h / 2);
    ctx.fillText('0ms', 2, h - 8);

    const maxPts = 35;
    const stepX = (w - 55) / (maxPts - 1);

    models.forEach(model => {
      const lats = latencyHistory[model.model_id] || [];
      if (lats.length < 2) return;

      const color = model.color || '#00f3ff';
      ctx.strokeStyle = color;
      ctx.lineWidth = 2;
      ctx.beginPath();

      const startOffset = maxPts - lats.length;
      for (let i = 0; i < lats.length; i++) {
        const x = 40 + (startOffset + i) * stepX;
        const normY = lats[i] / maxLat;
        const y = h - 20 - normY * (h - 40);

        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();

      // Glowing tip
      const lastX = 40 + (startOffset + lats.length - 1) * stepX;
      const lastY = h - 20 - (lats[lats.length - 1] / maxLat) * (h - 40);
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(lastX, lastY, 3.5, 0, Math.PI * 2);
      ctx.fill();
    });
  }, [latencyHistory, models]);

  // Draw Score Bars
  useEffect(() => {
    const canvas = scoreCanvasRef.current;
    if (!canvas || !models || models.length === 0) return;
    const ctx = canvas.getContext('2d');
    const w = canvas.width;
    const h = canvas.height;

    ctx.clearRect(0, 0, w, h);
    ctx.fillStyle = '#04070d';
    ctx.fillRect(0, 0, w, h);

    const barHeight = Math.min(22, (h - 20) / models.length);
    let maxVal = 5;

    models.forEach(m => {
      const val = isSnake ? (m.game_state?.score || 0) : (m.game_state?.lines_cleared || 0);
      if (val > maxVal) maxVal = val;
    });

    models.forEach((m, idx) => {
      const y = 10 + idx * (barHeight + 6);
      const score = isSnake ? (m.game_state?.score || 0) : (m.game_state?.lines_cleared || 0);
      const barWidth = Math.max(4, (score / maxVal) * (w - 145));

      ctx.fillStyle = '#94a3b8';
      ctx.font = '10px monospace';
      const shortName = (m.name || m.model_id).slice(0, 11);
      ctx.fillText(shortName, 5, y + barHeight * 0.7);

      ctx.fillStyle = m.color || '#00f3ff';
      ctx.beginPath();
      ctx.roundRect(85, y, barWidth, barHeight, 3);
      ctx.fill();

      ctx.fillStyle = '#fff';
      ctx.font = 'bold 10px monospace';
      ctx.fillText(`${score} ${isSnake ? 'pts' : 'lines'}`, 92 + barWidth, y + barHeight * 0.7);
    });
  }, [models, isSnake]);

  return (
    <section style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '16px' }}>
      <div style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border-color)',
        borderRadius: '10px',
        padding: '12px'
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          fontSize: '0.75rem',
          textTransform: 'uppercase',
          color: 'var(--text-muted)',
          fontFamily: 'var(--font-mono)',
          marginBottom: '8px'
        }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Activity size={14} color="var(--cyan-glow)" /> Step Latency Real-Time Stream (ms)
          </span>
          <span style={{ color: 'var(--cyan-glow)' }}>JEV sub-100ms vs LLM</span>
        </div>
        <canvas
          ref={latencyCanvasRef}
          width={450}
          height={150}
          style={{ width: '100%', height: '150px', display: 'block', borderRadius: '6px' }}
        />
      </div>

      <div style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border-color)',
        borderRadius: '10px',
        padding: '12px'
      }}>
        <div style={{
          fontSize: '0.75rem',
          textTransform: 'uppercase',
          color: 'var(--text-muted)',
          fontFamily: 'var(--font-mono)',
          marginBottom: '8px',
          display: 'flex',
          alignItems: 'center',
          gap: '6px'
        }}>
          <BarChart3 size={14} color="var(--purple-glow)" />
          <span>{isSnake ? '🍎 Cumulative Apples Eaten' : '🧱 Cumulative Lines Cleared'}</span>
        </div>
        <canvas
          ref={scoreCanvasRef}
          width={450}
          height={150}
          style={{ width: '100%', height: '150px', display: 'block', borderRadius: '6px' }}
        />
      </div>
    </section>
  );
}
