import React, { useState, useEffect, useRef, useCallback } from 'react';
import Header from './components/Header';
import ControlBar from './components/ControlBar';
import Leaderboard from './components/Leaderboard';
import ArenaGrid from './components/ArenaGrid';
import TelemetryCharts from './components/TelemetryCharts';
import HackerTerminal from './components/HackerTerminal';
import ModelInspectorModal from './components/ModelInspectorModal';
import { cyberAudio } from './audio';

export default function App() {
  const [gameMode, setGameMode] = useState('snake');
  const [status, setStatus] = useState('connecting');
  const [turn, setTurn] = useState(0);
  const [isRunning, setIsRunning] = useState(false);
  const [config, setConfig] = useState({
    width: 8,
    height: 8,
    seed: 42,
    maze_type: 'open',
    step_delay_ms: 300,
  });

  const [models, setModels] = useState([]);
  const [lastEvents, setLastEvents] = useState({});
  const [latencyHistory, setLatencyHistory] = useState({});
  const [logs, setLogs] = useState([]);
  const [selectedModel, setSelectedModel] = useState(null);
  const [isMuted, setIsMuted] = useState(false);

  const wsRef = useRef(null);
  const modelsMapRef = useRef({});

  // Connect WebSocket
  useEffect(() => {
    let reconnectTimer;

    const connect = () => {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = window.location.host;
      // In Vite dev mode, proxy /ws to localhost:8000
      const wsUrl = `${protocol}//${host}/ws`;

      setStatus('connecting');
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setStatus('connected');
      };

      ws.onclose = () => {
        setStatus('disconnected');
        reconnectTimer = setTimeout(connect, 2000);
      };

      ws.onerror = () => {
        setStatus('disconnected');
      };

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          handleWebSocketMessage(msg);
        } catch (e) {
          console.error('WS parse error:', e);
        }
      };
    };

    connect();

    return () => {
      if (reconnectTimer) clearTimeout(reconnectTimer);
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  const handleWebSocketMessage = useCallback((msg) => {
    if (msg.type === 'FULL_STATE') {
      const gMode = msg.game_mode || 'snake';
      setGameMode(gMode);
      setTurn(msg.turn || 0);
      setIsRunning(msg.is_running || false);
      if (msg.config) setConfig(msg.config);

      const mList = msg.models || [];
      setModels(mList);

      const mMap = {};
      mList.forEach(m => { mMap[m.model_id] = m; });
      modelsMapRef.current = mMap;

    } else if (msg.type === 'TICK') {
      setTurn(msg.turn);
      setIsRunning(msg.is_running);

      const events = msg.events || [];
      const newLastEvents = {};
      let anyScore = false;
      let anyCrashed = false;
      let tetrisLines = 0;

      events.forEach(ev => {
        newLastEvents[ev.model_id] = ev;

        // Audio checks
        if (ev.game_mode === 'snake') {
          if (ev.decision?.eats_food) anyScore = true;
        } else {
          if (ev.decision?.lines_cleared > 0) {
            anyScore = true;
            tetrisLines = Math.max(tetrisLines, ev.decision.lines_cleared);
          } else {
            cyberAudio.playPieceLock();
          }
        }

        if (!ev.game_state?.is_alive && ev.decision?.is_safe === false) {
          anyCrashed = true;
        }

        // Record latency
        if (ev.decision?.latency_ms !== undefined) {
          setLatencyHistory(prev => {
            const arr = prev[ev.model_id] || [];
            const nextArr = [...arr, ev.decision.latency_ms];
            if (nextArr.length > 35) nextArr.shift();
            return { ...prev, [ev.model_id]: nextArr };
          });
        }
      });

      // Sound triggers
      if (anyCrashed) cyberAudio.playCrash();
      else if (anyScore) {
        if (msg.game_mode === 'tetris') cyberAudio.playLineClear(tetrisLines);
        else cyberAudio.playFood();
      } else {
        cyberAudio.playStep();
      }

      setLastEvents(prev => ({ ...prev, ...newLastEvents }));
      setLogs(prev => [...prev.slice(-350), ...events]);

      // Update models list
      setModels(prev => prev.map(m => {
        const ev = newLastEvents[m.model_id];
        if (ev) {
          return {
            ...m,
            game_state: ev.game_state,
            telemetry: ev.telemetry,
          };
        }
        return m;
      }));

    } else if (msg.type === 'STATUS_CHANGE') {
      setIsRunning(msg.is_running);
    } else if (msg.type === 'GAME_OVER') {
      setIsRunning(false);
      cyberAudio.playCrash();
    }
  }, []);

  const send = (cmd) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(cmd));
    }
  };

  const handleSwitchGame = (targetMode) => {
    setGameMode(targetMode);
    cyberAudio.playStart();
    setLastEvents({});
    setLatencyHistory({});
    setLogs([]);
    send({ action: 'switch_game', game_type: targetMode });
  };

  const handlePlay = () => {
    cyberAudio.playStart();
    send({ action: 'play' });
  };

  const handlePause = () => {
    send({ action: 'pause' });
  };

  const handleStep = () => {
    send({ action: 'step' });
  };

  const handleReset = (overrides = {}) => {
    const updated = { ...config, ...overrides };
    setConfig(updated);
    setLastEvents({});
    setLatencyHistory({});
    setLogs([]);
    send({ action: 'reset', config: updated });
  };

  const handleUpdateConfig = (updates) => {
    const updated = { ...config, ...updates };
    setConfig(updated);
    send({ action: 'update_config', config: updated });
  };

  const handleToggleMute = () => {
    const muted = cyberAudio.toggleMute();
    setIsMuted(muted);
  };

  const handleExecuteCli = (rawCmd) => {
    const parts = rawCmd.split(' ');
    const action = parts[0].toLowerCase();

    if (action === 'help') {
      setLogs(prev => [...prev, {
        name: 'SYSTEM',
        model_id: 'system',
        color: '#00f3ff',
        turn: turn,
        decision: {
          direction: 'CLI_HELP',
          confidence: 1.0,
          latency_ms: 0,
          is_safe: true,
          reasoning: 'Commands: play, pause, step, reset, game tetris, game snake, seed <num>, clear'
        }
      }]);
    } else if (action === 'play') handlePlay();
    else if (action === 'pause') handlePause();
    else if (action === 'step') handleStep();
    else if (action === 'reset') handleReset();
    else if (action === 'clear') setLogs([]);
    else if (action === 'game' && parts[1]) {
      const g = parts[1].toLowerCase();
      if (g === 'tetris' || g === 'snake') handleSwitchGame(g);
    } else if (action === 'seed' && parts[1]) {
      const s = parseInt(parts[1]);
      handleReset({ seed: s });
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Header
        gameMode={gameMode}
        setGameMode={handleSwitchGame}
        turn={turn}
        seed={config.seed || 42}
        status={status}
        isMuted={isMuted}
        onToggleMute={handleToggleMute}
      />

      <ControlBar
        gameMode={gameMode}
        isRunning={isRunning}
        onPlay={handlePlay}
        onPause={handlePause}
        onStep={handleStep}
        onReset={handleReset}
        config={config}
        onUpdateConfig={handleUpdateConfig}
      />

      <main style={{ flex: 1, padding: '20px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <Leaderboard
          gameMode={gameMode}
          models={models}
          onSelectModel={setSelectedModel}
        />

        <ArenaGrid
          gameMode={gameMode}
          models={models}
          lastEvents={lastEvents}
          onSelectModel={setSelectedModel}
          speedDelayMs={config.step_delay_ms || 300}
        />

        <TelemetryCharts
          gameMode={gameMode}
          models={models}
          latencyHistory={latencyHistory}
        />

        <HackerTerminal
          logs={logs}
          onExecuteCommand={handleExecuteCli}
        />
      </main>

      <ModelInspectorModal
        model={selectedModel}
        lastEvent={selectedModel ? lastEvents[selectedModel.model_id] : null}
        onClose={() => setSelectedModel(null)}
      />
    </div>
  );
}
