import { useState, useEffect, useCallback, useRef } from 'react';
import { AGENTS, STATUS } from '../utils/constants';

const initialAgentState = () =>
  AGENTS.reduce((acc, agent) => {
    acc[agent.id] = {
      status: STATUS.IDLE,
      progress: 0,
      message: '',
      result: null,
      duration: null,
      error: null,
      startedAt: null,
    };
    return acc;
  }, {});

export function useAgents(addListener) {
  const [agents, setAgents] = useState(initialAgentState);
  const [pipelineStatus, setPipelineStatus] = useState('idle'); // idle | running | completed | error
  const [pipelineSummary, setPipelineSummary] = useState(null);
  const [logs, setLogs] = useState([]);

  const addLog = useCallback((entry) => {
    setLogs((prev) => [
      { ...entry, id: Date.now() + Math.random(), time: new Date().toLocaleTimeString() },
      ...prev,
    ].slice(0, 200));
  }, []);

  const resetAgents = useCallback(() => {
    setAgents(initialAgentState());
    setPipelineStatus('idle');
    setPipelineSummary(null);
    setLogs([]);
  }, []);

  useEffect(() => {
    if (!addListener) return;

    const removeListener = addListener((event) => {
      switch (event.event) {
        case 'agent_started':
          setAgents((prev) => ({
            ...prev,
            [event.agent]: {
              ...prev[event.agent],
              status: STATUS.RUNNING,
              progress: 0,
              message: 'Iniciando...',
              error: null,
              result: null,
              startedAt: event.timestamp,
            },
          }));
          setPipelineStatus('running');
          addLog({ type: 'info', agent: event.agent, text: 'Agente iniciado' });
          break;

        case 'agent_progress':
          setAgents((prev) => ({
            ...prev,
            [event.agent]: {
              ...prev[event.agent],
              progress: event.progress || prev[event.agent]?.progress || 0,
              message: event.message || '',
            },
          }));
          addLog({ type: 'progress', agent: event.agent, text: event.message });
          break;

        case 'agent_completed':
          setAgents((prev) => ({
            ...prev,
            [event.agent]: {
              ...prev[event.agent],
              status: STATUS.SUCCESS,
              progress: 100,
              message: 'Completado',
              result: event.result,
              duration: event.duration,
            },
          }));
          addLog({
            type: 'success',
            agent: event.agent,
            text: `Completado en ${event.duration?.toFixed(1)}s`,
          });
          break;

        case 'agent_error':
          setAgents((prev) => ({
            ...prev,
            [event.agent]: {
              ...prev[event.agent],
              status: STATUS.ERROR,
              progress: 0,
              message: 'Error',
              error: event.error,
            },
          }));
          setPipelineStatus('error');
          addLog({ type: 'error', agent: event.agent, text: event.error });
          break;

        case 'pipeline_completed':
          setPipelineStatus('completed');
          setPipelineSummary(event.summary);
          addLog({ type: 'success', agent: null, text: 'Pipeline completado' });
          break;

        default:
          break;
      }
    });

    return removeListener;
  }, [addListener, addLog]);

  // Computed stats
  const stats = {
    totalVulnerabilities: Object.values(agents).reduce((sum, a) => {
      if (a.result?.vulnerabilities) return sum + a.result.vulnerabilities.length;
      if (a.result?.issues_count) return sum + a.result.issues_count;
      if (a.result?.findings) return sum + a.result.findings.length;
      if (a.result?.hallazgos) return sum + a.result.hallazgos.length;
      if (a.result?.resumen) return sum + a.result.resumen.length;
      return sum;
    }, 0),
    openPorts: (() => {
      const psResult = agents.port_scanner?.result;
      if (!psResult) return 0;
      if (psResult.open_ports) return psResult.open_ports.length;
      if (psResult.ports_count) return psResult.ports_count;
      if (psResult.stdout) {
        const matches = psResult.stdout.match(/open/gi);
        return matches ? matches.length : 0;
      }
      return 0;
    })(),
    secretsFound: agents.secret_detector?.result?.total_secretos ||
                  agents.secret_detector?.result?.secrets_count ||
                  agents.secret_detector?.result?.findings?.length || 
                  agents.secret_detector?.result?.hallazgos?.length || 0,
    issuesCreated: agents.github_reporter?.result?.raw_output ? 1 : 
                   (agents.github_reporter?.result?.issues_created || 0),
    completedAgents: Object.values(agents).filter((a) => a.status === STATUS.SUCCESS).length,
    failedAgents: Object.values(agents).filter((a) => a.status === STATUS.ERROR).length,
    runningAgents: Object.values(agents).filter((a) => a.status === STATUS.RUNNING).length,
  };

  return {
    agents,
    pipelineStatus,
    pipelineSummary,
    stats,
    logs,
    resetAgents,
  };
}

export default useAgents;
