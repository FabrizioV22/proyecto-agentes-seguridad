import './TargetConfig.css';

const FIELDS = [
  {
    key: 'target_ip',
    label: 'Target IP',
    icon: '🔍',
    placeholder: '192.168.1.1',
    hint: 'Dirección IP para escaneo de puertos (Nmap)',
  },
  {
    key: 'target_url',
    label: 'Target URL',
    icon: '🌐',
    placeholder: 'https://example.com',
    hint: 'URL para auditoría web (SQLMap)',
  },
  {
    key: 'target_path',
    label: 'Target Path',
    icon: '📁',
    placeholder: '/path/to/project',
    hint: 'Ruta del proyecto para análisis de código, secretos y dependencias',
  },
];

export default function TargetConfig({ config, onConfigChange }) {
  const handleChange = (key, value) => {
    onConfigChange({ ...config, [key]: value });
  };

  return (
    <div className="target-config">
      <h3 className="target-config-title">🎯 Configuración de Objetivos</h3>
      <p className="target-config-desc">
        Define los objetivos que serán analizados por los agentes de seguridad.
      </p>
      <div className="target-config-grid">
        {FIELDS.map((field) => (
          <div key={field.key} className="target-config-field">
            <label className="target-config-label">
              <span className="target-config-label-icon">{field.icon}</span>
              {field.label}
            </label>
            <input
              className="target-config-input"
              type="text"
              value={config[field.key] || ''}
              onChange={(e) => handleChange(field.key, e.target.value)}
              placeholder={field.placeholder}
              spellCheck="false"
            />
            <span className="target-config-hint">{field.hint}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
