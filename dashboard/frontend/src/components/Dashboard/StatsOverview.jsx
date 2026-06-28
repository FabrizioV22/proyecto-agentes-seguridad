import { useEffect, useRef } from 'react';
import './StatsOverview.css';

function AnimatedNumber({ value }) {
  const ref = useRef(null);
  const prevRef = useRef(0);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const start = prevRef.current;
    const end = value;
    const duration = 600;
    const startTime = performance.now();

    function animate(now) {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3); // easeOutCubic
      el.textContent = Math.round(start + (end - start) * eased);
      if (progress < 1) requestAnimationFrame(animate);
    }

    requestAnimationFrame(animate);
    prevRef.current = end;
  }, [value]);

  return <span ref={ref}>{value}</span>;
}

const STATS_CONFIG = [
  {
    key: 'totalVulnerabilities',
    label: 'Vulnerabilidades',
    icon: '🛡️',
    color: '#ef4444',
    bg: 'rgba(239, 68, 68, 0.1)',
  },
  {
    key: 'openPorts',
    label: 'Puertos Abiertos',
    icon: '🔓',
    color: '#06b6d4',
    bg: 'rgba(6, 182, 212, 0.1)',
  },
  {
    key: 'secretsFound',
    label: 'Secretos Detectados',
    icon: '🔑',
    color: '#f59e0b',
    bg: 'rgba(245, 158, 11, 0.1)',
  },
  {
    key: 'issuesCreated',
    label: 'Issues Creados',
    icon: '📋',
    color: '#10b981',
    bg: 'rgba(16, 185, 129, 0.1)',
  },
];

export default function StatsOverview({ stats }) {
  return (
    <div className="stats-overview">
      {STATS_CONFIG.map((cfg) => (
        <div
          key={cfg.key}
          className="stat-card"
          style={{ '--stat-color': cfg.color, '--stat-bg': cfg.bg }}
        >
          <div className="stat-card-header">
            <div className="stat-card-icon" style={{ background: cfg.bg }}>
              {cfg.icon}
            </div>
          </div>
          <div className="stat-card-value">
            <AnimatedNumber value={stats[cfg.key] || 0} />
          </div>
          <div className="stat-card-label">{cfg.label}</div>
        </div>
      ))}
    </div>
  );
}
