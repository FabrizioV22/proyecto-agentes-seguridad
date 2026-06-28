export const AGENTS = [
  {
    id: 'port_scanner',
    name: 'Escáner de Puertos',
    description: 'Escaneo de puertos y servicios con Nmap',
    icon: '🔍',
    tool: 'Nmap',
    color: '#06b6d4',
    order: 1,
  },
  {
    id: 'web_auditor',
    name: 'Auditor Web',
    description: 'Detección de inyecciones SQL con SQLMap',
    icon: '🌐',
    tool: 'SQLMap',
    color: '#8b5cf6',
    order: 2,
  },
  {
    id: 'code_scanner',
    name: 'Escáner de Código',
    description: 'Análisis estático de código con Bandit',
    icon: '📝',
    tool: 'Bandit',
    color: '#f59e0b',
    order: 3,
  },
  {
    id: 'secret_detector',
    name: 'Detector de Secretos',
    description: 'Detección de credenciales y secretos con Gitleaks',
    icon: '🔑',
    tool: 'Gitleaks',
    color: '#ef4444',
    order: 4,
  },
  {
    id: 'dependency_auditor',
    name: 'Auditor de Dependencias',
    description: 'Escaneo de vulnerabilidades en dependencias con Safety',
    icon: '📦',
    tool: 'Safety',
    color: '#10b981',
    order: 5,
  },
  {
    id: 'github_reporter',
    name: 'Reporte GitHub',
    description: 'Creación automática de issues en GitHub con hallazgos',
    icon: '📊',
    tool: 'GitHub API',
    color: '#3b82f6',
    order: 6,
  },
];

export const AGENT_MAP = AGENTS.reduce((acc, agent) => {
  acc[agent.id] = agent;
  return acc;
}, {});

export const STATUS = {
  IDLE: 'idle',
  RUNNING: 'running',
  SUCCESS: 'success',
  ERROR: 'error',
  SKIPPED: 'skipped',
};

export const SEVERITY_ORDER = {
  CRITICAL: 0,
  HIGH: 1,
  MEDIUM: 2,
  LOW: 3,
  INFO: 4,
};

export const VIEWS = {
  DASHBOARD: 'dashboard',
  RESULTS: 'results',
  CONFIG: 'config',
};

export const API_BASE = '/api';
export const WS_URL = `ws://${window.location.hostname}:8000/ws`;

export const DEFAULT_CONFIG = {
  target_ip: '',
  target_url: '',
  target_path: '',
  enabled_agents: AGENTS.map((a) => a.id),
};
