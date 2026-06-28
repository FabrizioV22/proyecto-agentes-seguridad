import { AGENTS } from '../../utils/constants';
import './AgentToggle.css';

export default function AgentToggle({ enabledAgents, onToggle }) {
  const handleToggle = (agentId) => {
    const isEnabled = enabledAgents.includes(agentId);
    if (isEnabled) {
      onToggle(enabledAgents.filter((id) => id !== agentId));
    } else {
      onToggle([...enabledAgents, agentId]);
    }
  };

  return (
    <div className="agent-toggle-list">
      <h3 className="agent-toggle-title">🤖 Agentes del Pipeline</h3>
      <p className="agent-toggle-desc">
        Activa o desactiva los agentes que deseas incluir en la ejecución del pipeline.
      </p>

      {AGENTS.map((agent) => {
        const isEnabled = enabledAgents.includes(agent.id);
        return (
          <div
            key={agent.id}
            className={`agent-toggle-item ${!isEnabled ? 'disabled' : ''}`}
          >
            <div className="agent-toggle-icon">{agent.icon}</div>
            <div className="agent-toggle-info">
              <div className="agent-toggle-name">{agent.name}</div>
              <div className="agent-toggle-description">{agent.description}</div>
              <span className="agent-toggle-tool">{agent.tool}</span>
            </div>
            <label className="toggle">
              <input
                type="checkbox"
                checked={isEnabled}
                onChange={() => handleToggle(agent.id)}
              />
              <span className="toggle-slider" />
            </label>
          </div>
        );
      })}
    </div>
  );
}
