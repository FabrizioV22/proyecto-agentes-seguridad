import { useState, useEffect } from 'react';
import './Header.css';

const STATUS_LABELS = {
  idle: 'Inactivo',
  running: 'Ejecutando',
  completed: 'Completado',
  error: 'Error',
};

export default function Header({ pipelineStatus, isConnected }) {
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const formattedTime = time.toLocaleTimeString('es-ES', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });

  return (
    <header className="header">
      <div className="header-left">
        <div>
          <div className="header-title">Security Agents Dashboard</div>
          <div className="header-subtitle">Pipeline de auditoría automatizada</div>
        </div>
        <span className={`header-pipeline-badge ${pipelineStatus}`}>
          {pipelineStatus === 'running' && '⟳ '}
          {STATUS_LABELS[pipelineStatus] || pipelineStatus}
        </span>
      </div>

      <div className="header-right">
        <div className="header-connection">
          <span
            className={`header-connection-dot ${isConnected ? 'connected' : 'disconnected'}`}
          />
          <span>{isConnected ? 'WS Conectado' : 'Desconectado'}</span>
        </div>
        <div className="header-clock">{formattedTime}</div>
      </div>
    </header>
  );
}
