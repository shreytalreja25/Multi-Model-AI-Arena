import React from 'react';
import { Trophy, ShieldCheck, ShieldAlert } from 'lucide-react';

export default function Leaderboard({ gameMode, models, onSelectModel, safetyStatus }) {
  const isSnake = gameMode === 'snake';
  const isTetris = gameMode === 'tetris';
  const isChess = gameMode === 'chess';
  const isDino = gameMode === 'dino';

  // Sort models
  const sorted = [...models].sort((a, b) => {
    if (isSnake) {
      const scoreA = a.game_state?.score || 0;
      const scoreB = b.game_state?.score || 0;
      if (scoreB !== scoreA) return scoreB - scoreA;
      const stepsA = a.game_state?.steps || 0;
      const stepsB = b.game_state?.steps || 0;
      if (stepsB !== stepsA) return stepsB - stepsA;
    } else if (isTetris) {
      const linesA = a.game_state?.lines_cleared || 0;
      const linesB = b.game_state?.lines_cleared || 0;
      if (linesB !== linesA) return linesB - linesA;
      const piecesA = a.game_state?.pieces_placed || 0;
      const piecesB = b.game_state?.pieces_placed || 0;
      if (piecesB !== piecesA) return piecesB - piecesA;
    } else if (isChess) {
      // Chess: Material balance first, then total moves
      const matA = a.game_state?.material_diff || 0;
      const matB = b.game_state?.material_diff || 0;
      if (matB !== matA) return matB - matA;
      const movesA = a.game_state?.total_moves || 0;
      const movesB = b.game_state?.total_moves || 0;
      if (movesB !== movesA) return movesB - movesA;
    } else {
      // Dino: distance traveled first, then obstacles cleared
      const distA = a.game_state?.distance || 0;
      const distB = b.game_state?.distance || 0;
      if (distB !== distA) return distB - distA;
      const obsA = a.game_state?.obstacles_cleared || 0;
      const obsB = b.game_state?.obstacles_cleared || 0;
      if (obsB !== obsA) return obsB - obsA;
    }

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
              <th style={{ padding: '6px 12px' }}>
                {isSnake ? 'Score (Apples)' : isTetris ? 'Lines Cleared' : isChess ? 'Material Balance' : 'Distance Traveled'}
              </th>
              <th style={{ padding: '6px 12px' }}>
                {isSnake ? 'Steps Survived' : isTetris ? 'Pieces Placed' : isChess ? 'Moves Played' : 'Obstacles Cleared'}
              </th>
              <th style={{ padding: '6px 12px' }}>Avg Latency</th>
              <th style={{ padding: '6px 12px' }}>P50 Latency</th>
              <th style={{ padding: '6px 12px' }}>Token Cost ($)</th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((m, idx) => {
              const rank = idx === 0 ? '🥇' : (idx === 1 ? '🥈' : (idx === 2 ? '🥉' : `#${idx + 1}`));
              const isAlive = m.game_state?.is_alive !== false;
              const isGemini = m.model_id.includes('gemini');
              const isCircuitBroken = isGemini && safetyStatus?.is_circuit_broken;

              let statusText = isAlive ? 'ACTIVE' : (m.game_state?.death_reason || m.game_state?.termination || 'DEAD').replace('_', ' ').toUpperCase();
              let statusClass = isAlive ? 'alive' : 'crashed';

              if (isCircuitBroken) {
                statusText = 'AUTO-DISABLED (BREAKER)';
                statusClass = 'crashed';
              }

              const avgLat = m.telemetry?.avg_latency_ms || 0;
              const p50Lat = m.telemetry?.p50_latency_ms || avgLat;
              const latColor = avgLat < 120 ? 'var(--green-glow)' : (avgLat > 1500 ? 'var(--amber-glow)' : 'var(--cyan-glow)');
              const cost = m.telemetry?.total_cost_usd > 0 ? `$${m.telemetry.total_cost_usd.toFixed(6)}` : '$0.00';

              const primaryMetric = isSnake
                ? (m.game_state?.score || 0)
                : isTetris
                ? `${m.game_state?.lines_cleared || 0} lines`
                : isChess
                ? (m.game_state?.material_diff > 0 ? `+${m.game_state?.material_diff} MAT` : `${m.game_state?.material_diff || 0} MAT`)
                : `${Math.floor(m.game_state?.distance || 0)}m`;

              const secondaryMetric = isSnake
                ? (m.game_state?.steps || 0)
                : isTetris
                ? (m.game_state?.pieces_placed || 0)
                : isChess
                ? `${m.game_state?.total_moves || 0} moves (${m.telemetry?.record || '0W/0L'})`
                : `${m.game_state?.obstacles_cleared || 0} cleared (${m.game_state?.speed ? m.game_state.speed.toFixed(1) : 6.0} px/f)`;

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
                      {isGemini && (
                        <span style={{
                          fontSize: '0.62rem',
                          padding: '1px 5px',
                          borderRadius: '3px',
                          background: 'rgba(66, 133, 244, 0.15)',
                          border: '1px solid #4285F4',
                          color: '#4285F4'
                        }}>
                          CIRCUIT BREAKER
                        </span>
                      )}
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
                  <td style={{ padding: '8px 12px' }}>{p50Lat}ms</td>
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
