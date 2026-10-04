import React from 'react';
import { X, Cpu, ShieldAlert, FileText, Code2 } from 'lucide-react';

export default function ModelInspectorModal({ model, lastEvent, onClose }) {
  if (!model) return null;

  const dec = lastEvent?.decision || model.telemetry?.last_decision || {};
  const stateRepr = lastEvent?.state_repr || {};
  const probs = dec.probabilities || {};
  const dirs = ['UP', 'DOWN', 'LEFT', 'RIGHT'];
  const critMap = stateRepr.criteria || {};

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        background: 'rgba(0, 0, 0, 0.78)',
        backdropFilter: 'blur(10px)',
        zIndex: 100,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '20px'
      }}
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div style={{
        background: '#0a0f1d',
        border: '1px solid var(--cyan-glow)',
        boxShadow: '0 0 35px rgba(0, 243, 255, 0.25)',
        borderRadius: '12px',
        width: '100%',
        maxWidth: '820px',
        maxHeight: '90vh',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden'
      }}>
        {/* Header */}
        <div style={{
          padding: '14px 20px',
          background: '#0f172a',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Cpu size={20} color="var(--cyan-glow)" />
            <span style={{ fontSize: '1.05rem', fontWeight: 800 }}>{model.name}</span>
            <span style={{
              fontSize: '0.68rem',
              fontFamily: 'var(--font-mono)',
              padding: '2px 8px',
              borderRadius: '4px',
              background: 'rgba(0, 243, 255, 0.15)',
              color: 'var(--cyan-glow)',
              border: '1px solid rgba(0, 243, 255, 0.3)'
            }}>
              {model.model_type?.toUpperCase()}
            </span>
          </div>

          <button
            onClick={onClose}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--text-muted)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              padding: '4px'
            }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Body */}
        <div style={{ padding: '20px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '16px' }}>
            {/* Probabilities */}
            <div style={{
              background: 'rgba(15, 23, 42, 0.7)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              borderRadius: '8px',
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
                <Cpu size={14} color="var(--cyan-glow)" /> Decision Probabilities
              </div>

              {dirs.map(d => {
                const val = probs[d] !== undefined ? probs[d] : (dec.direction === d ? dec.confidence : 0.05);
                const pct = Math.round(val * 100);
                const isChosen = dec.direction === d;
                const color = isChosen ? (model.color || '#00f3ff') : 'rgba(255,255,255,0.4)';

                return (
                  <div key={d} style={{ display: 'flex', alignItems: 'center', gap: '10px', fontFamily: 'var(--font-mono)', fontSize: '0.8rem', marginBottom: '6px' }}>
                    <span style={{ width: '45px', fontWeight: 'bold', color: isChosen ? color : '#94a3b8' }}>{d}</span>
                    <div style={{ flex: 1, height: '10px', background: 'rgba(255, 255, 255, 0.08)', borderRadius: '5px', overflow: 'hidden' }}>
                      <div style={{ width: `${pct}%`, height: '100%', background: color, transition: 'width 0.3s ease' }}></div>
                    </div>
                    <span style={{ width: '40px', textAlign: 'right', color: isChosen ? '#fff' : '#64748b' }}>{pct}%</span>
                  </div>
                );
              })}
            </div>

            {/* Criteria & Hazards */}
            <div style={{
              background: 'rgba(15, 23, 42, 0.7)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              borderRadius: '8px',
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
                <ShieldAlert size={14} color="var(--amber-glow)" /> Spatial Criteria & Hazards
              </div>

              {Object.keys(critMap).length > 0 ? (
                Object.entries(critMap).map(([k, text]) => (
                  <div key={k} style={{ fontSize: '0.74rem', marginBottom: '6px', fontFamily: 'var(--font-mono)', color: dec.direction?.includes(k) ? '#38bdf8' : '#94a3b8' }}>
                    <strong style={{ color: 'var(--cyan-glow)' }}>{k}:</strong> {text}
                  </div>
                ))
              ) : (
                <div style={{ fontSize: '0.74rem', color: '#94a3b8', fontStyle: 'italic' }}>
                  {dec.reasoning || 'Evaluated safe moves and distance vectors'}
                </div>
              )}
            </div>
          </div>

          {/* ASCII Board */}
          <div style={{
            background: 'rgba(15, 23, 42, 0.7)',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            borderRadius: '8px',
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
              <FileText size={14} color="var(--purple-glow)" /> Verbatim ASCII Board Map
            </div>
            <pre style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '0.74rem',
              lineHeight: 1.25,
              background: '#030508',
              padding: '10px',
              borderRadius: '6px',
              color: '#38bdf8',
              overflowX: 'auto',
              margin: 0
            }}>
              {stateRepr.ascii_grid || '(Board state will appear upon step)'}
            </pre>
          </div>

          {/* Raw JSON */}
          <div style={{
            background: 'rgba(15, 23, 42, 0.7)',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            borderRadius: '8px',
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
              <Code2 size={14} color="var(--green-glow)" /> Raw Telemetry & Decision JSON
            </div>
            <pre style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '0.72rem',
              background: '#030508',
              padding: '10px',
              borderRadius: '6px',
              maxHeight: '140px',
              overflowY: 'auto',
              color: '#94a3b8',
              margin: 0
            }}>
              {JSON.stringify({ decision: dec, telemetry: model.telemetry }, null, 2)}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
}
