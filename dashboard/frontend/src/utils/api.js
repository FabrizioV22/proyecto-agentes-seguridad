import { API_BASE } from './constants';

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }
    return await response.json();
  } catch (err) {
    if (err.name === 'TypeError' && err.message === 'Failed to fetch') {
      throw new Error('No se pudo conectar con el servidor backend');
    }
    throw err;
  }
}

export const api = {
  // Pipeline
  startPipeline: (config) =>
    request('/pipeline/start', {
      method: 'POST',
      body: JSON.stringify(config),
    }),

  stopPipeline: () =>
    request('/pipeline/stop', {
      method: 'POST',
    }),

  getPipelineStatus: () => request('/pipeline/status'),

  // Agents
  getAgents: () => request('/agents'),

  runAgent: (agentId) =>
    request(`/agents/${agentId}/run`, {
      method: 'POST',
    }),

  // Results
  getResults: () => request('/results'),

  getAgentResults: (agentId) => request(`/results/${agentId}`),
};

export default api;
