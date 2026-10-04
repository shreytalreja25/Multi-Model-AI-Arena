import React from 'react';
import { Volume2, VolumeX, Activity, Sparkles } from 'lucide-react';

export default function Header({
  gameMode,
  setGameMode,
  turn,
  seed,
  status,
  isMuted,
  onToggleMute,
}) {
  const isSnake = gameMode === 'snake';

  return (
    <header style={{
      padding: '12px 24px',
      background: 'rgba(9, 13, 23, 0.92)',
      backdropFilter: 'blur(16px)',
      borderBottom: '1px solid var(--border-color)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      position: 'sticky',
      top: 0,
      zIndex: 50,
      boxShadow: '0 4px 20px rgba(0,0,0,0.5)'
    }}>
      {/* Logo & Title */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
        <div style={{
          fontSize: '28px',
          animation: 'pulseGlow 2.5s infinite',
          lineHeight: 1
        }}>
          {isSnake ? '🐍' : '🧱'}
        </div>
        <div>
          <h1 style={{
            fontSize: '1.18rem',
            letterSpacing: '0.08em',
            fontWeight: 800,
            textTransform: 'uppercase',
            background: 'linear-gradient(90deg, #00f3ff, #a855f7)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            margin: 0
          }}>
            {isSnake ? 'Cyber-Snake AI Arena' : 'Cyber-Tetris AI Arena'}
          </h1>
          <div style={{
            fontSize: '0.72rem',
            fontFamily: 'var(--font-mono)',
            color: 'var(--text-muted)',
            letterSpacing: '0.05em'
          }}>
            JEV 1.13 SYSTEM-ONE vs LAYA vs OLLAMA LOCAL LLMS
          </div>
        </div>
      </div>

      {/* Game Mode Tabs */}
      <div style={{
        display: 'flex',
        gap: '6px',
        background: 'rgba(0, 0, 0, 0.5)',
        padding: '4px',
        borderRadius: '8px',
        border: '1px solid rgba(255, 255, 255, 0.08)'
      }}>
        <button
          className={`cyber-btn ${isSnake ? 'active' : ''}`}
          onClick={() => setGameMode('snake')}
          style={{ padding: '6px 14px' }}
        >
          <span>🐍</span> CYBER-SNAKE
        </button>
        <button
          className={`cyber-btn ${!isSnake ? 'active' : ''}`}
          onClick={() => setGameMode('tetris')}
          style={{ padding: '6px 14px' }}
        >
          <span>🧱</span> CYBER-TETRIS
        </button>
      </div>

      {/* Status & Telemetry HUD */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px', fontFamily: 'var(--font-mono)', fontSize: '0.8rem' }}>
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '6px',
          padding: '4px 10px',
          borderRadius: '9999px',
          background: status === 'connected' ? 'rgba(16, 185, 129, 0.12)' : 'rgba(239, 68, 68, 0.12)',
          border: `1px solid ${status === 'connected' ? 'rgba(16, 185, 129, 0.35)' : 'rgba(239, 68, 68, 0.35)'}`,
          color: status === 'connected' ? '#34d399' : '#f87171'
        }}>
          <span style={{
            width: '7px',
            height: '7px',
            borderRadius: '50%',
            background: 'currentColor',
            boxShadow: '0 0 8px currentColor'
          }}></span>
          <span>{status === 'connected' ? 'ONLINE [WS 8000]' : 'CONNECTING...'}</span>
        </div>

        <div style={{
          padding: '4px 10px',
          borderRadius: '6px',
          background: 'rgba(255, 255, 255, 0.05)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          color: 'var(--text-secondary)'
        }}>
          TURN: <span style={{ color: 'var(--cyan-glow)', fontWeight: 'bold' }}>{turn}</span>
        </div>

        <div style={{
          padding: '4px 10px',
          borderRadius: '6px',
          background: 'rgba(255, 255, 255, 0.05)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          color: 'var(--text-secondary)'
        }}>
          SEED: <span style={{ color: 'var(--purple-glow)', fontWeight: 'bold' }}>{seed}</span>
        </div>

        <button
          className={`cyber-btn ${!isMuted ? 'active' : ''}`}
          onClick={onToggleMute}
          title={isMuted ? 'Unmute Audio' : 'Mute Audio'}
        >
          {isMuted ? <VolumeX size={15} /> : <Volume2 size={15} />}
          <span>{isMuted ? 'MUTED' : 'AUDIO'}</span>
        </button>
      </div>
    </header>
  );
}
