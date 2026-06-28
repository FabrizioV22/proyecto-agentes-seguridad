import StatusIndicator from './StatusIndicator';
import { AGENT_MAP } from '../../utils/constants';
import './AgentCard.css';

function getResultSummary(agentId, result) {
  if (!result) return null;
  switch (agentId) {
    case 'port_scanner':
      return `${result.open_ports?.length || result.ports_count || 0} puertos abiertos`;
    case 'web_auditor':
      return `${result.vulnerabilities?.length || result.issues_count || 0} vulnerabilidades`;
    case 'code_scanner':
      return `${result.findings?.length || result.issues_count || 0} hallazgos`;
    case 'secret_detector':
      return `${result.secrets_count || result.findings?.length || 0} secretos`;
    case 'dependency_auditor':
      return `${result.vulnerabilities?.length || result.issues_count || 0} deps vulnerables`;
    case 'github_reporter':
      return `${result.issues_created || 0} issues creados`;
    default:
      return null;
  }
}

export default function AgentCard({ agentId, state, onRun, style }) {
  const agent = AGENT_MAP[agentId];
  if (!agent) return null;

  const { status, progress, message, result, duration, error } = state;
  const summary = getResultSummary(agentId, result);

  return (
    <div className={`agent-card ${status}`} style={style}>
      {status === 'running' && <div className="scan-line" />}

      <div className="agent-card-header">
        <span className="agent-card-icon">{agent.icon}</span>
        <div className="agent-card-title">
          <h4>{agent.name}</h4>
          <span className="agent-tool">{agent.tool}</span>
        </div>
        <div className="agent-card-status">
          <StatusIndicator status={status} />
        </div>
      </div>

      <div className="agent-card-body">
        <p className="agent-card-message">
          {error ? `❌ ${error}` : message || agent.description}
        </p>

        {(status === 'running' || status === 'success') && (
          <div className="agent-progress-bar">
            <div
              className={`agent-progress-fill ${status === 'running' ? 'running' : ''}`}
              style={{ width: `${progress}%` }}
            />
          </div>
        )}
      </div>

      <div className="agent-card-footer">
        <span className="agent-card-result-summary">
          {summary && <span className="text-cyan">{summary}</span>}
        </span>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {duration != null && (
            <span className="agent-card-duration">{duration.toFixed(1)}s</span>
          )}
          {status === 'idle' && onRun && (
            <button className="agent-card-run-btn" onClick={() => onRun(agentId)}>
              Ejecutar
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
