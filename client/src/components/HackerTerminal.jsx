import React, { useState, useRef, useEffect } from 'react';
import { Terminal, Download, Search, CheckSquare, Square } from 'lucide-react';

export default function HackerTerminal({ logs, onExecuteCommand }) {
  const [filter, setFilter] = useState('ALL');
  const [search, setSearch] = useState('');
  const [autoScroll, setAutoScroll] = useState(true);
  const [cliInput, setCliInput] = useState('');
  const bodyRef = useRef(null);

  // Auto-scroll
  useEffect(() => {
    if (autoScroll && bodyRef.current) {
      bodyRef.current.scrollTop = bodyRef.current.scrollHeight;
    }
  }, [logs, autoScroll]);

  const filteredLogs = logs.filter(l => {
    if (filter !== 'ALL') {
      const mId = (l.model_id || '').toLowerCase();
      if (!mId.includes(filter.toLowerCase())) return false;
    }
    if (search.trim()) {
      const q = search.toLowerCase();
      const str = JSON.stringify(l).toLowerCase();
      if (!str.includes(q)) return false;
    }
    return true;
  });

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      const cmd = cliInput.trim();
      setCliInput('');
      if (cmd) onExecuteCommand(cmd);
    }
  };

  const exportJson = () => {
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(logs, null, 2));
    const a = document.createElement('a');
    a.href = dataStr;
    a.download = `cyber_arena_telemetry_${Date.now()}.json`;
    a.click();
  };

  const exportCsv = () => {
    const headers = ['Turn', 'GameMode', 'ModelID', 'ModelName', 'Action', 'Confidence', 'LatencyMs', 'Reasoning'];
    const rows = logs.map(l => [
      l.turn,
      `"${l.game_mode || 'snake'}"`,
      `"${l.model_id}"`,
      `"${l.name}"`,
      `"${l.decision?.direction || ''}"`,
      l.decision?.confidence || 0,
      l.decision?.latency_ms || 0,
      `"${(l.decision?.reasoning || '').replace(/"/g, '""')}"`,
    ]);
    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
    const a = document.createElement('a');
    a.href = encodeURI(csvContent);
    a.download = `cyber_arena_telemetry_${Date.now()}.csv`;
    a.click();
  };

  return (
    <section style={{
      background: '#04070d',
      border: '1px solid rgba(0, 243, 255, 0.25)',
      borderRadius: '10px',
      overflow: 'hidden',
      boxShadow: '0 4px 24px rgba(0, 0, 0, 0.6)'
    }}>
      {/* Terminal Top Bar */}
      <div style={{
        padding: '10px 16px',
        background: '#090f1a',
        borderBottom: '1px solid rgba(0, 243, 255, 0.15)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '10px'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          fontFamily: 'var(--font-mono)',
          fontSize: '0.8rem',
          color: 'var(--cyan-glow)',
          fontWeight: 700
        }}>
          <Terminal size={16} color="#34d399" />
          <span>RESEARCH PROTOCOL_STREAM // TELEMETRY STDOUT</span>
        </div>

        {/* Filter & Search Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', gap: '4px' }}>
            {['ALL', 'jev', 'laya', 'qwen', 'llama', 'algo'].map(f => (
              <button
                key={f}
                className={`cyber-btn ${filter === f ? 'active' : ''}`}
                onClick={() => setFilter(f)}
                style={{ padding: '3px 8px', fontSize: '0.72rem' }}
              >
                {f.toUpperCase()}
              </button>
            ))}
          </div>

          <div style={{ display: 'flex', alignItems: 'center', position: 'relative' }}>
            <input
              type="text"
              className="cyber-input"
              placeholder="Search logs..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{ width: '130px', padding: '3px 8px', fontSize: '0.75rem' }}
            />
          </div>

          <label style={{
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            cursor: 'pointer',
            fontSize: '0.75rem',
            fontFamily: 'var(--font-mono)',
            color: 'var(--text-secondary)'
          }}>
            <input
              type="checkbox"
              checked={autoScroll}
              onChange={(e) => setAutoScroll(e.target.checked)}
              style={{ accentColor: 'var(--cyan-glow)' }}
            />
            Auto
          </label>

          <button className="cyber-btn" onClick={exportJson} style={{ padding: '3px 8px', fontSize: '0.7rem' }}>
            <Download size={13} /> JSON
          </button>
          <button className="cyber-btn" onClick={exportCsv} style={{ padding: '3px 8px', fontSize: '0.7rem' }}>
            <Download size={13} /> CSV
          </button>
        </div>
      </div>

      {/* Terminal Body */}
      <div
        ref={bodyRef}
        style={{
          height: '220px',
          overflowY: 'auto',
          padding: '10px 16px',
          fontFamily: 'var(--font-mono)',
          fontSize: '0.74rem',
          lineHeight: '1.55',
          color: '#cbd5e1',
          display: 'flex',
          flexDirection: 'column',
          gap: '3px',
          background: '#04070d'
        }}
      >
        {filteredLogs.length === 0 ? (
          <div style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>
            Awaiting streaming protocol events... Run arena to start telemetry stream.
          </div>
        ) : (
          filteredLogs.map((ev, i) => {
            const dec = ev.decision || {};
            const dir = dec.direction || 'NONE';
            const conf = dec.confidence !== undefined ? `${Math.round(dec.confidence * 100)}%` : '--';
            const lat = dec.latency_ms !== undefined ? `${dec.latency_ms}ms` : '--';
            const badgeColor = ev.color || '#00f3ff';
            const shortName = ev.name ? ev.name.split(' ')[0].toUpperCase() : 'MODEL';

            return (
              <div key={i} style={{ display: 'flex', gap: '8px', alignItems: 'baseline', wordBreak: 'break-all' }}>
                <span style={{ color: 'var(--text-muted)', flexShrink: 0 }}>
                  [T:{ev.turn}]
                </span>
                <span style={{
                  fontWeight: 700,
                  padding: '1px 5px',
                  borderRadius: '3px',
                  fontSize: '0.68rem',
                  flexShrink: 0,
                  background: `${badgeColor}22`,
                  color: badgeColor,
                  border: `1px solid ${badgeColor}44`
                }}>
                  [{shortName}]
                </span>
                <span style={{
                  fontWeight: 700,
                  flexShrink: 0,
                  color: dec.is_safe ? '#34d399' : '#f87171'
                }}>
                  {dir}
                </span>
                <span style={{ color: 'var(--cyan-glow)', flexShrink: 0 }}>
                  conf:{conf} lat:{lat}
                </span>
                <span style={{ color: 'var(--text-secondary)' }}>
                  "{dec.reasoning || ''}"
                </span>
              </div>
            );
          })
        )}
      </div>

      {/* Interactive CLI Input */}
      <div style={{
        background: '#090f1a',
        borderTop: '1px solid rgba(255,255,255,0.06)',
        padding: '6px 12px',
        display: 'flex',
        alignItems: 'center',
        gap: '8px'
      }}>
        <span style={{ color: 'var(--cyan-glow)', fontFamily: 'var(--font-mono)', fontSize: '0.8rem', fontWeight: 'bold' }}>
          cyber@arena:~$
        </span>
        <input
          type="text"
          placeholder="type 'help', 'play', 'pause', 'game tetris', 'game snake', 'clear'..."
          value={cliInput}
          onChange={(e) => setCliInput(e.target.value)}
          onKeyDown={handleKeyDown}
          style={{
            background: 'transparent',
            border: 'none',
            color: '#f8fafc',
            fontFamily: 'var(--font-mono)',
            fontSize: '0.8rem',
            outline: 'none',
            flex: 1
          }}
        />
      </div>
    </section>
  );
}
