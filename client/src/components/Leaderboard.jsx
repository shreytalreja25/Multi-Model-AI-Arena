import React from 'react';
import { Trophy, Zap, AlertCircle } from 'lucide-react';

export default function Leaderboard({ gameMode, models, onSelectModel }) {
  const isSnake = gameMode === 'snake';

  // Sort models
  const sorted = [...models].sort((a, b) => {
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

  return (
    <section style={{
      background: 'var(--bg-card)',
      backdropFilter: 'blur(12px)',
      border: '1px solid var(--border-color)',
      borderRadius: '10px',
      padding: '14px 18px',
      boxShadow: '0 4px 20px rgba(0,0,0,0.4)'
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '12px',
        borderBottom: '1px solid rgba(255, 255, 255, 0.06)',
        paddingBottom: '8px'
      }}>
        <div style={{
          fontSize: '0.88rem',
          fontWeight: 700,
          textTransform: 'uppercase',
          letterSpacing: '0.08em',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <Trophy size={16} color="var(--cyan-glow)" />
          <span>Real-Time Model Telemetry & Leaderboard</span>
          <span style={{
            fontSize: '0.68rem',
            padding: '2px 7px',
            borderRadius: '4px',
            background: 'rgba(0, 243, 255, 0.15)',
            color: 'var(--cyan-glow)',
            border: '1px solid rgba(0, 243, 255, 0.3)'
          }}>
            IDENTICAL SEED COMPARISON
          </span>
        </div>
        <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.72rem', color: 'var(--text-muted)' }}>
          Click any model to inspect live decision vectors
        </div>
      </div>

      <div style={{ overflowX: 'auto' }}>
        <table style={{
          width: '100%',
          borderCollapse: 'collapse',
          fontFamily: 'var(--font-mono)',
          fontSize: '0.8rem',
          textAlign: 'left'
        }}>
          <thead>
            <tr style={{ color: 'var(--text-muted)', fontSize: '0.7rem', textTransform: 'uppercase', borderBottom: '1px solid rgba(255, 255, 255, 0.08)' }}>
              <th style={{ padding: '6px 12px' }}>Rank</th>
              <th style={{ padding: '6px 12px' }}>Model Architecture</th>
              <th style={{ padding: '6px 12px' }}>Status</th>
              <th style={{ padding: '6px 12px' }}>{isSnake ? 'Score (Apples)' : 'Lines Cleared'}</th>
              <th style={{ padding: '6px 12px' }}>{isSnake ? 'Steps Survived' : 'Pieces Placed'}</th>
              <th style={{ padding: '6px 12px' }}>Avg Latency</th>
              <th style={{ padding: '6px 12px' }}>P99 Latency</th>
              <th style={{ padding: '6px 12px' }}>Token Cost ($)</th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((m, idx) => {
              const rank = idx === 0 ? '🥇' : (idx === 1 ? '🥈' : (idx === 2 ? '🥉' : `#${idx + 1}`));
              const isAlive = m.game_state?.is_alive !== false;
              const statusClass = isAlive ? 'alive' : 'crashed';
              const statusText = isAlive ? 'ALIVE' : (m.game_state?.death_reason || 'DEAD').replace('_', ' ').toUpperCase();
              const avgLat = m.telemetry?.avg_latency_ms || 0;
              const latColor = avgLat < 120 ? 'var(--green-glow)' : (avgLat > 1500 ? 'var(--amber-glow)' : 'var(--cyan-glow)');
              const cost = m.telemetry?.total_cost_usd > 0 ? `$${m.telemetry.total_cost_usd.toFixed(6)}` : '$0.00';

              const primaryMetric = isSnake
                ? (m.game_state?.score || 0)
                : `${m.game_state?.lines_cleared || 0} lines (${m.game_state?.score || 0} pts)`;

              const secondaryMetric = isSnake
                ? (m.game_state?.steps || 0)
                : (m.game_state?.pieces_placed || 0);

              return (
                <tr
                  key={m.model_id}
                  onClick={() => onSelectModel(m)}
                  style={{
                    cursor: 'pointer',
                    borderBottom: '1px solid rgba(255, 255, 255, 0.04)',
                    transition: 'background 0.15s ease'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.04)'}
                  onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                >
                  <td style={{ padding: '8px 12px', fontWeight: 'bold' }}>{rank}</td>
                  <td style={{ padding: '8px 12px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 700 }}>
                      <span style={{
                        width: '8px',
                        height: '8px',
                        borderRadius: '50%',
                        background: m.color || '#00f3ff',
                        boxShadow: `0 0 8px ${m.color || '#00f3ff'}`
                      }}></span>
                      <span>{m.name}</span>
                    </div>
                  </td>
                  <td style={{ padding: '8px 12px' }}>
                    <span className={`badge-tag ${statusClass}`}>{statusText}</span>
                  </td>
                  <td style={{ padding: '8px 12px', color: 'var(--cyan-glow)', fontWeight: 'bold' }}>
                    {primaryMetric}
                  </td>
                  <td style={{ padding: '8px 12px' }}>{secondaryMetric}</td>
                  <td style={{ padding: '8px 12px', color: latColor, fontWeight: 'bold' }}>
                    {avgLat}ms
                  </td>
                  <td style={{ padding: '8px 12px' }}>{m.telemetry?.p99_latency_ms || 0}ms</td>
                  <td style={{ padding: '8px 12px' }}>{cost}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}
