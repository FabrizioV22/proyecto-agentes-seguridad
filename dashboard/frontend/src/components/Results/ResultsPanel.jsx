import { useState } from 'react';
import { AGENTS, AGENT_MAP, STATUS } from '../../utils/constants';
import StatusIndicator from '../Dashboard/StatusIndicator';
import VulnerabilityCard from './VulnerabilityCard';
import JsonViewer from './JsonViewer';
import './ResultsPanel.css';

function extractVulnerabilities(agentId, result) {
  if (!result) return [];

  // Helper to map Spanish keys to English keys for the card
  const mapFinding = (item) => ({
    title: item.title || item.codigo || item.regla || item.name || 'Hallazgo de seguridad',
    description: item.description || item.detalle || item.descripcion || item.codigo || undefined,
    severity: item.severity || item.severidad || 'INFO',
    file: item.file || item.archivo || item.filename || undefined,
    line: item.line || item.linea || item.linea_inicio || undefined,
    recommendation: item.recommendation || item.recomendacion || undefined,
    ...item
  });

  // Try common result shapes
  if (result.vulnerabilities && Array.isArray(result.vulnerabilities)) {
    return result.vulnerabilities.map(mapFinding);
  }
  if (result.findings && Array.isArray(result.findings)) {
    return result.findings.map(mapFinding);
  }
  if (result.hallazgos && Array.isArray(result.hallazgos)) {
    return result.hallazgos.map(mapFinding);
  }
  if (result.resumen && Array.isArray(result.resumen)) {
    return result.resumen.map(str => ({
      title: 'Hallazgo SQLMap',
      description: str,
      severity: str.toLowerCase().includes('vulnerable') ? 'HIGH' : 'INFO'
    }));
  }
  if (result.results && Array.isArray(result.results)) {
    return result.results.map(mapFinding);
  }
  if (result.open_ports && Array.isArray(result.open_ports)) {
    return result.open_ports.map((p) => ({
      title: `Puerto ${p.port || p} abierto`,
      severity: 'MEDIUM',
      port: p.port || p,
      description: p.service ? `Servicio: ${p.service}` : undefined,
    }));
  }
  if (result.puertos_abiertos && Array.isArray(result.puertos_abiertos)) {
    return result.puertos_abiertos.map((p) => ({
      title: `Puerto ${p.puerto || p} abierto`,
      severity: 'MEDIUM',
      port: p.puerto || p,
      description: p.servicio ? `Servicio: ${p.servicio}` : undefined,
    }));
  }
  if (agentId === 'port_scanner' && result.stdout) {
    // Attempt to extract open ports from nmap output
    const lines = result.stdout.split('\n');
    const openPorts = [];
    for (const line of lines) {
      if (line.includes('open')) {
        const parts = line.trim().split(/\s+/);
        if (parts.length >= 3 && parts[0].includes('/')) {
          openPorts.push({
            title: `Puerto ${parts[0]} abierto`,
            severity: 'MEDIUM',
            port: parts[0],
            description: `Servicio: ${parts.slice(2).join(' ')}`,
          });
        }
      }
    }
    return openPorts;
  }
  if (result.issues && Array.isArray(result.issues)) {
    return result.issues;
  }
  if (agentId === 'github_reporter' && result.raw_output) {
    return [{
      title: 'Issue Creado',
      severity: 'INFO',
      description: result.raw_output
    }];
  }
  return [];
}


export default function ResultsPanel({ agents }) {
  const [activeTab, setActiveTab] = useState(AGENTS[0].id);
  const [showRaw, setShowRaw] = useState(false);

  const currentAgent = AGENT_MAP[activeTab];
  const currentState = agents[activeTab] || {};
  const vulnerabilities = extractVulnerabilities(activeTab, currentState.result);

  return (
    <div className="results-panel">
      <h2 className="results-panel-title">📋 Resultados del Análisis</h2>

      <div className="results-tabs">
        {AGENTS.map((agent) => {
          const state = agents[agent.id] || {};
          return (
            <button
              key={agent.id}
              className={`results-tab ${activeTab === agent.id ? 'active' : ''}`}
              onClick={() => { setActiveTab(agent.id); setShowRaw(false); }}
            >
              <span className="results-tab-icon">{agent.icon}</span>
              <span>{agent.name}</span>
              <span className={`results-tab-dot ${state.status || 'idle'}`} />
            </button>
          );
        })}
      </div>

      <div className="results-content">
        <div className="results-content-header">
          <div className="results-content-agent-status">
            <StatusIndicator status={currentState.status || 'idle'} />
            <span className="results-content-agent-name">
              {currentAgent?.icon} {currentAgent?.name}
            </span>
            {currentState.duration != null && (
              <span className="badge badge-info" style={{ marginLeft: 8 }}>
                {currentState.duration.toFixed(1)}s
              </span>
            )}
          </div>

          <button className="results-toggle-raw" onClick={() => setShowRaw(!showRaw)}>
            {showRaw ? '← Vista formateada' : 'Ver JSON crudo →'}
          </button>
        </div>

        {currentState.status === STATUS.ERROR && (
          <div className="results-error">
            ❌ Error: {currentState.error || 'Error desconocido'}
          </div>
        )}

        {!currentState.result && currentState.status !== STATUS.ERROR && (
          <div className="results-empty">
            <div className="results-empty-icon">
              {currentState.status === STATUS.RUNNING ? '⏳' : '📭'}
            </div>
            <div className="results-empty-text">
              {currentState.status === STATUS.RUNNING
                ? 'Análisis en progreso...'
                : 'No hay resultados todavía. Ejecuta el pipeline para ver los hallazgos.'}
            </div>
          </div>
        )}

        {currentState.result && !showRaw && (
          <div>
            {vulnerabilities.length > 0 ? (
              <>
                <div className="results-section-title">
                  {vulnerabilities.length} hallazgo{vulnerabilities.length !== 1 ? 's' : ''} encontrado{vulnerabilities.length !== 1 ? 's' : ''}
                </div>
                <div className="results-vuln-list">
                  {vulnerabilities.map((vuln, idx) => (
                    <VulnerabilityCard key={idx} vulnerability={vuln} />
                  ))}
                </div>
              </>
            ) : (
              <div className="results-empty">
                <div className="results-empty-icon">✅</div>
                <div className="results-empty-text">
                  No se encontraron hallazgos. El resultado está disponible en formato JSON.
                </div>
                <button
                  className="results-toggle-raw"
                  onClick={() => setShowRaw(true)}
                  style={{ marginTop: 16 }}
                >
                  Ver JSON crudo →
                </button>
              </div>
            )}
          </div>
        )}

        {currentState.result && showRaw && (
          <>
            <div className="results-section-title">Respuesta JSON del Agente</div>
            <JsonViewer data={currentState.result} />
          </>
        )}
      </div>
    </div>
  );
}
