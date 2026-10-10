import React from 'react';
import SnakeCanvas from './SnakeCanvas';
import TetrisCanvas from './TetrisCanvas';
import ChessCanvas from './ChessCanvas';
import DinoCanvas from './DinoCanvas';
import { Eye } from 'lucide-react';

export default function ArenaGrid({
  gameMode,
  models,
  lastEvents,
  onSelectModel,
  speedDelayMs = 300,
}) {
  const isSnake = gameMode === 'snake';
  const isTetris = gameMode === 'tetris';
  const isChess = gameMode === 'chess';
  const isDino = gameMode === 'dino';

  return (
    <section style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingBottom: '4px'
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
          <span>🎮 Live Concurrent Viewports</span>
          <span style={{
            fontSize: '0.68rem',
            padding: '2px 7px',
            borderRadius: '4px',
            background: 'rgba(16, 185, 129, 0.15)',
            color: '#34d399',
            border: '1px solid rgba(16, 185, 129, 0.3)'
          }}>
            60 FPS SMOOTH ENGINE
          </span>
        </div>
        <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.72rem', color: 'var(--text-muted)' }}>
          Click card to inspect neural activation & criteria
        </div>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(290px, 1fr))',
        gap: '16px'
      }}>
        {models.map(model => {
          const mId = model.model_id;
          const ev = lastEvents[mId] || {};
          const dec = ev.decision || model.telemetry?.last_decision || {};
          const isAlive = model.game_state?.is_alive !== false;
          const lat = dec.latency_ms !== undefined ? `${dec.latency_ms}ms` : '-- ms';
          const conf = dec.confidence !== undefined ? `${Math.round(dec.confidence * 100)}%` : '--%';
          const badgeColor = model.color || '#00f3ff';

          const primaryVal = isSnake
            ? (model.game_state?.score || 0)
            : isTetris
            ? (model.game_state?.lines_cleared || 0)
            : isChess
            ? (model.game_state?.material_diff > 0 ? `+${model.game_state?.material_diff}` : model.game_state?.material_diff || 0)
            : (model.game_state?.distance !== undefined ? `${Math.floor(model.game_state.distance)}m` : 0);

          const secondaryVal = isSnake
            ? (model.game_state?.steps || 0)
            : isTetris
            ? (model.game_state?.pieces_placed || 0)
            : isChess
            ? (model.game_state?.total_moves || 0)
            : (model.game_state?.speed ? `${model.game_state.speed.toFixed(1)} px` : '--');

          return (
            <div
              key={mId}
              onClick={() => onSelectModel(model)}
              style={{
                background: 'var(--bg-card)',
                backdropFilter: 'blur(12px)',
                border: '1px solid var(--border-color)',
                borderRadius: '12px',
                padding: '14px',
                display: 'flex',
                flexDirection: 'column',
                gap: '10px',
                transition: 'all 0.2s ease',
                position: 'relative',
                overflow: 'hidden',
                cursor: 'pointer',
                boxShadow: '0 4px 16px rgba(0,0,0,0.3)'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = badgeColor;
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = `0 8px 24px ${badgeColor}33`;
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = 'var(--border-color)';
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '0 4px 16px rgba(0,0,0,0.3)';
              }}
            >
              {/* Card Header */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{
                    width: '8px',
                    height: '8px',
                    borderRadius: '50%',
                    background: badgeColor,
                    boxShadow: `0 0 8px ${badgeColor}`
                  }}></span>
                  <span style={{ fontSize: '0.88rem', fontWeight: 700 }}>{model.name}</span>
                  <span style={{
                    fontSize: '0.65rem',
                    fontFamily: 'var(--font-mono)',
                    padding: '2px 6px',
                    borderRadius: '4px',
                    background: 'rgba(255, 255, 255, 0.08)',
                    color: 'var(--text-secondary)'
                  }}>
                    {model.model_type?.toUpperCase()}
                  </span>
                </div>

                <span style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: '0.72rem',
                  fontWeight: 700,
                  padding: '2px 8px',
                  borderRadius: '4px',
                  background: 'rgba(0, 0, 0, 0.5)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  color: badgeColor
                }}>
                  {lat}
                </span>
              </div>

              {/* Viewport Canvas Container */}
              <div style={{
                width: '100%',
                aspectRatio: isSnake ? '1 / 1' : isTetris ? '10 / 18' : '1 / 1',
                background: '#03060a',
                borderRadius: '8px',
                border: '1px solid rgba(255, 255, 255, 0.08)',
                overflow: 'hidden',
                position: 'relative',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                {isSnake ? (
                  <SnakeCanvas
                    gameState={model.game_state}
                    modelColor={badgeColor}
                    isAlive={isAlive}
                  />
                ) : isTetris ? (
                  <TetrisCanvas
                    gameState={model.game_state}
                    decision={ev.decision}
                    preGrid={ev.pre_grid}
                    modelColor={badgeColor}
                    isAlive={isAlive}
                    speedDelayMs={speedDelayMs}
                  />
                ) : isChess ? (
                  <ChessCanvas
                    gameState={model.game_state}
                    lastEvent={ev}
                    modelColor={badgeColor}
                    width={270}
                    height={270}
                  />
                ) : (
                  <DinoCanvas
                    gameState={model.game_state}
                    lastEvent={ev}
                    modelColor={badgeColor}
                    isAlive={isAlive}
                    width={300}
                    height={190}
                  />
                )}

                {/* Dead Overlay for Snake */}
                {!isAlive && isSnake && (
                  <div style={{
                    position: 'absolute',
                    top: '8px',
                    right: '8px',
                    background: 'rgba(239, 68, 68, 0.85)',
                    color: '#fff',
                    fontFamily: 'var(--font-mono)',
                    fontSize: '0.72rem',
                    fontWeight: 700,
                    padding: '3px 8px',
                    borderRadius: '4px',
                    pointerEvents: 'none'
                  }}>
                    DEAD: {(model.game_state?.death_reason || 'CRASH').replace('_', ' ').toUpperCase()}
                  </div>
                )}
              </div>

              {/* Stats Row */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(3, 1fr)',
                gap: '6px',
                fontFamily: 'var(--font-mono)',
                fontSize: '0.75rem',
                background: 'rgba(0, 0, 0, 0.35)',
                padding: '8px 10px',
                borderRadius: '6px',
                border: '1px solid rgba(255, 255, 255, 0.04)'
              }}>
                <div>
                  <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>
                    {isSnake ? 'SCORE' : isTetris ? 'LINES' : isChess ? 'MATERIAL' : 'DISTANCE'}
                  </div>
                  <div style={{ fontWeight: 700, color: 'var(--text-primary)' }}>{primaryVal}</div>
                </div>
                <div>
                  <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>
                    {isSnake ? 'STEPS' : isTetris ? 'PIECES' : isChess ? 'MOVES' : 'SPEED'}
                  </div>
                  <div style={{ fontWeight: 700, color: 'var(--text-primary)' }}>{secondaryVal}</div>
                </div>
                <div>
                  <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>
                    {isChess ? 'RECORD' : isDino ? 'CLEARED' : 'CONFIDENCE'}
                  </div>
                  <div style={{ fontWeight: 700, color: isChess ? badgeColor : isDino ? '#10b981' : 'var(--cyan-glow)' }}>
                    {isChess ? (model.telemetry?.record || '0W/0D/0L') : isDino ? (model.game_state?.obstacles_cleared || 0) : conf}
                  </div>
                </div>
              </div>

              {/* Reasoning Ticker */}
              <div style={{
                fontSize: '0.72rem',
                fontFamily: 'var(--font-mono)',
                color: 'var(--text-muted)',
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                padding: '4px 6px',
                background: 'rgba(0, 0, 0, 0.25)',
                borderRadius: '4px'
              }}>
                {dec.reasoning || (isChess ? `White move: ${dec.san || 'waiting...'}` : 'Awaiting tick...')}
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
