import { useState } from 'react';
import { AGENTS, VIEWS } from '../../utils/constants';
import StatusIndicator from '../Dashboard/StatusIndicator';
import './Sidebar.css';

const NAV_ITEMS = [
  { view: VIEWS.DASHBOARD, icon: '📊', label: 'Dashboard' },
  { view: VIEWS.RESULTS, icon: '📋', label: 'Resultados' },
  { view: VIEWS.CONFIG, icon: '⚙️', label: 'Configuración' },
];

export default function Sidebar({ currentView, onViewChange, agents }) {
  const [isOpen, setIsOpen] = useState(false);

  const handleNavClick = (view) => {
    onViewChange(view);
    setIsOpen(false);
  };

  return (
    <>
      <button
        className="sidebar-toggle"
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Toggle menu"
      >
        {isOpen ? '✕' : '☰'}
      </button>

      <div className={`sidebar-overlay ${isOpen ? 'visible' : ''}`} onClick={() => setIsOpen(false)} />

      <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
        <div className="sidebar-logo">
          <div className="sidebar-logo-icon">🛡️</div>
          <div>
            <div className="sidebar-logo-text">SecPipeline</div>
            <div className="sidebar-logo-version">v1.0.0</div>
          </div>
        </div>

        <nav className="sidebar-nav">
          <div className="sidebar-nav-section">
            <div className="sidebar-nav-section-title">Navegación</div>
            {NAV_ITEMS.map((item) => (
              <div
                key={item.view}
                className={`sidebar-nav-item ${currentView === item.view ? 'active' : ''}`}
                onClick={() => handleNavClick(item.view)}
              >
                <span className="sidebar-nav-item-icon">{item.icon}</span>
                <span>{item.label}</span>
              </div>
            ))}
          </div>
        </nav>

        <div className="sidebar-agents">
          <div className="sidebar-nav-section-title">Agentes</div>
          {AGENTS.map((agent) => {
            const state = agents?.[agent.id];
            return (
              <div key={agent.id} className="sidebar-agent-item">
                <span className="sidebar-agent-icon">{agent.icon}</span>
                <span className="sidebar-agent-name">{agent.name}</span>
                <StatusIndicator status={state?.status || 'idle'} size="sm" />
              </div>
            );
          })}
        </div>
      </aside>
    </>
  );
}
