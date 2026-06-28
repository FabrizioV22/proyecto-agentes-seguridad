import { useState, useCallback } from 'react';
import { AGENTS, VIEWS, DEFAULT_CONFIG } from './utils/constants';
import api from './utils/api';
import useWebSocket from './hooks/useWebSocket';
import useAgents from './hooks/useAgents';
import Sidebar from './components/Layout/Sidebar';
import Header from './components/Layout/Header';
import PipelineTimeline from './components/Dashboard/PipelineTimeline';
import StatsOverview from './components/Dashboard/StatsOverview';
import AgentCard from './components/Dashboard/AgentCard';
import TargetConfig from './components/Config/TargetConfig';
import AgentToggle from './components/Config/AgentToggle';
import ResultsPanel from './components/Results/ResultsPanel';
import './App.css';

const LOG_TYPE_ICONS = {
  info: 'ℹ️',
  progress: '⟳',
  success: '✅',
  error: '❌',
};

export default function App() {
  const [currentView, setCurrentView] = useState(VIEWS.DASHBOARD);
  const [config, setConfig] = useState(DEFAULT_CONFIG);
  const [isStarting, setIsStarting] = useState(false);

  const { isConnected, addListener } = useWebSocket();
  const { agents, pipelineStatus, stats, logs, resetAgents } = useAgents(addListener);

  const handleStartPipeline = useCallback(async () => {
    try {
      setIsStarting(true);
      await api.startPipeline(config);
    } catch (err) {
      console.error('Failed to start pipeline:', err);
      alert(`Error al iniciar pipeline: ${err.message}`);
    } finally {
      setIsStarting(false);
    }
  }, [config]);

  const handleStopPipeline = useCallback(async () => {
    try {
      await api.stopPipeline();
    } catch (err) {
      console.error('Failed to stop pipeline:', err);
    }
  }, []);

  const handleRunAgent = useCallback(async (agentId) => {
    try {
      await api.runAgent(agentId);
    } catch (err) {
      console.error(`Failed to run agent ${agentId}:`, err);
    }
  }, []);

  const isRunning = pipelineStatus === 'running';

  return (
    <div className="app-layout">
      <Sidebar
        currentView={currentView}
        onViewChange={setCurrentView}
        agents={agents}
      />

      <div className="app-main">
        <Header pipelineStatus={pipelineStatus} isConnected={isConnected} />

        <div className="app-content">
          {/* ─── Dashboard View ─── */}
          {currentView === VIEWS.DASHBOARD && (
            <div className="dashboard-view">
              {/* Pipeline Controls */}
              <div className="pipeline-controls">
                {!isRunning ? (
                  <>
                    <button
                      className="pipeline-start-btn"
                      onClick={handleStartPipeline}
                      disabled={isStarting || !isConnected}
                    >
                      {isStarting ? (
                        <>
                          <span className="animate-spin" style={{ display: 'inline-block' }}>⟳</span>
                          Iniciando...
                        </>
                      ) : (
                        <>🚀 Iniciar Pipeline</>
                      )}
                    </button>
                    {pipelineStatus === 'completed' && (
                      <button className="pipeline-reset-btn" onClick={resetAgents}>
                        ↺ Reiniciar
                      </button>
                    )}
                  </>
                ) : (
                  <button className="pipeline-stop-btn" onClick={handleStopPipeline}>
                    ◼ Detener Pipeline
                  </button>
                )}
              </div>

              {/* Pipeline Timeline */}
              <PipelineTimeline agents={agents} />

              {/* Stats */}
              <StatsOverview stats={stats} />

              {/* Agent Cards Grid */}
              <div className="dashboard-agents-grid">
                {AGENTS.map((agent, idx) => (
                  <AgentCard
                    key={agent.id}
                    agentId={agent.id}
                    state={agents[agent.id] || {}}
                    onRun={handleRunAgent}
                    style={{ animationDelay: `${0.05 * idx}s` }}
                  />
                ))}
              </div>

              {/* Live Log Feed */}
              {logs.length > 0 && (
                <div className="log-feed">
                  <div className="log-feed-title">📜 Log de Actividad</div>
                  {logs.slice(0, 30).map((entry) => (
                    <div key={entry.id} className={`log-entry ${entry.type}`}>
                      <span className="log-entry-time">{entry.time}</span>
                      <span className="log-entry-type">
                        {LOG_TYPE_ICONS[entry.type] || '•'}
                      </span>
                      <span className="log-entry-text">
                        {entry.agent && (
                          <strong style={{ color: 'var(--accent-cyan)', marginRight: 6 }}>
                            [{AGENTS.find((a) => a.id === entry.agent)?.name || entry.agent}]
                          </strong>
                        )}
                        {entry.text}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* ─── Results View ─── */}
          {currentView === VIEWS.RESULTS && (
            <ResultsPanel agents={agents} />
          )}

          {/* ─── Config View ─── */}
          {currentView === VIEWS.CONFIG && (
            <div className="config-view">
              <div className="view-header">
                <h2 className="view-title">⚙️ Configuración</h2>
              </div>
              <TargetConfig config={config} onConfigChange={setConfig} />
              <AgentToggle
                enabledAgents={config.enabled_agents}
                onToggle={(agents) =>
                  setConfig((prev) => ({ ...prev, enabled_agents: agents }))
                }
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
