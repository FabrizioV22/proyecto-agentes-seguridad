import { AGENTS, STATUS } from '../../utils/constants';
import './PipelineTimeline.css';

export default function PipelineTimeline({ agents }) {
  const getConnectorState = (idx) => {
    if (idx >= AGENTS.length - 1) return { width: '0%', active: false };
    const current = agents[AGENTS[idx].id];
    const next = agents[AGENTS[idx + 1].id];

    if (current?.status === STATUS.SUCCESS && (next?.status === STATUS.RUNNING || next?.status === STATUS.SUCCESS || next?.status === STATUS.ERROR)) {
      return { width: '100%', active: next?.status === STATUS.RUNNING };
    }
    if (current?.status === STATUS.SUCCESS) {
      return { width: '50%', active: false };
    }
    if (current?.status === STATUS.RUNNING) {
      return { width: '0%', active: true };
    }
    return { width: '0%', active: false };
  };

  return (
    <div className="pipeline-timeline">
      <div className="pipeline-timeline-title">Pipeline de Seguridad</div>
      <div className="timeline-track">
        {AGENTS.map((agent, idx) => {
          const state = agents[agent.id] || {};
          const status = state.status || STATUS.IDLE;
          const connector = idx < AGENTS.length - 1 ? getConnectorState(idx) : null;

          return (
            <div key={agent.id} style={{ display: 'contents' }}>
              <div className={`timeline-node ${status}`}>
                <div className="timeline-node-circle">
                  {status === STATUS.SUCCESS && (
                    <span className="timeline-check">✓</span>
                  )}
                  {status === STATUS.ERROR && (
                    <span className="timeline-error-mark">✕</span>
                  )}
                  <span>{agent.icon}</span>
                </div>
                <span className="timeline-node-label">{agent.name}</span>
              </div>

              {connector !== null && (
                <div className={`timeline-connector ${connector.active ? 'active' : ''}`}>
                  <div
                    className="timeline-connector-fill"
                    style={{ width: connector.width }}
                  />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
