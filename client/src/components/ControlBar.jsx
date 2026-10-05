import React from 'react';
import { Play, Pause, StepForward, RotateCcw, Dices, Sliders } from 'lucide-react';

export default function ControlBar({
  gameMode,
  isRunning,
  onPlay,
  onPause,
  onStep,
  onReset,
  config,
  onUpdateConfig,
}) {
  const isSnake = gameMode === 'snake';
  const isTetris = gameMode === 'tetris';
  const isChess = gameMode === 'chess';

  const handleRandomSeed = () => {
    const newSeed = Math.floor(Math.random() * 90000) + 10000;
    onUpdateConfig({ seed: newSeed });
    onReset({ seed: newSeed });
  };

  return (
    <section style={{
      padding: '10px 24px',
      background: 'rgba(12, 16, 26, 0.95)',
      borderBottom: '1px solid var(--border-color)',
      display: 'flex',
      flexWrap: 'wrap',
      alignItems: 'center',
      justifyContent: 'space-between',
      gap: '14px',
    }}>
      {/* Playback Controls */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <button
          className={`cyber-btn btn-play ${isRunning ? 'running' : ''}`}
          onClick={isRunning ? onPause : onPlay}
          style={{ minWidth: '130px', justifyContent: 'center' }}
        >
          {isRunning ? <Pause size={16} /> : <Play size={16} />}
          <span>{isRunning ? 'PAUSE' : 'RUN ARENA'}</span>
        </button>

        <button className="cyber-btn" onClick={onStep} title="Step forward 1 turn">
          <StepForward size={16} />
          <span>STEP</span>
        </button>

        <button className="cyber-btn" onClick={() => onReset()} title="Reset Arena">
          <RotateCcw size={16} />
          <span>RESET</span>
        </button>
      </div>

      {/* Configuration Group */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '14px',
        fontSize: '0.82rem',
        fontFamily: 'var(--font-mono)',
        color: 'var(--text-secondary)'
      }}>
        {/* Snake-only Config */}
        {isSnake && (
          <>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <label style={{ color: 'var(--text-muted)' }}>GRID:</label>
              <select
                className="cyber-select"
                value={config.width || 8}
                onChange={(e) => {
                  const val = parseInt(e.target.value);
                  onUpdateConfig({ width: val, height: val });
                  onReset({ width: val, height: val });
                }}
              >
                <option value={6}>6x6 Micro</option>
                <option value={8}>8x8 Small (Default)</option>
                <option value={10}>10x10 Medium</option>
                <option value={12}>12x12 Large</option>
                <option value={16}>16x16 Arena</option>
              </select>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <label style={{ color: 'var(--text-muted)' }}>MAZE:</label>
              <select
                className="cyber-select"
                value={config.maze_type || 'open'}
                onChange={(e) => {
                  onUpdateConfig({ maze_type: e.target.value });
                  onReset({ maze_type: e.target.value });
                }}
              >
                <option value="open">Open Arena</option>
                <option value="cross">Central Cross</option>
                <option value="four_rooms">Four Rooms</option>
                <option value="corridors">Labyrinth Corridors</option>
                <option value="random_obstacles">Random Obstacles (10%)</option>
              </select>
            </div>
          </>
        )}

        {/* Tetris-only Config */}
        {isTetris && (
          <div style={{
            padding: '3px 8px',
            background: 'rgba(255, 255, 255, 0.05)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: '4px',
            fontSize: '0.74rem',
            color: 'var(--cyan-glow)'
          }}>
            MATRIX: 10x20 STANDARD (7-BAG RANDOMIZER)
          </div>
        )}

        {/* Chess-only Config */}
        {isChess && (
          <div style={{
            padding: '3px 8px',
            background: 'rgba(255, 255, 255, 0.05)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: '4px',
            fontSize: '0.74rem',
            color: 'var(--purple-glow)'
          }}>
            MATCH: AI (WHITE) vs MINIMAX BENCHMARK (BLACK)
          </div>
        )}

        {/* Seed Input */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <label style={{ color: 'var(--text-muted)' }}>SEED:</label>
          <input
            type="number"
            className="cyber-input"
            value={config.seed || 42}
            onChange={(e) => onUpdateConfig({ seed: parseInt(e.target.value) || 42 })}
            onBlur={() => onReset()}
            style={{ width: '75px' }}
          />
          <button className="cyber-btn" onClick={handleRandomSeed} title="Generate Random Seed">
            <Dices size={15} />
          </button>
        </div>

        {/* Speed Slider */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <label style={{ color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <Sliders size={14} /> SPEED:
          </label>
          <input
            type="range"
            min={50}
            max={1000}
            step={50}
            value={config.step_delay_ms || 300}
            onChange={(e) => onUpdateConfig({ step_delay_ms: parseInt(e.target.value) })}
            style={{ width: '90px', accentColor: 'var(--cyan-glow)', cursor: 'pointer' }}
          />
          <span style={{ color: 'var(--cyan-glow)', minWidth: '45px', fontWeight: 600 }}>
            {config.step_delay_ms || 300}ms
          </span>
        </div>
      </div>
    </section>
  );
}
