import './StatusIndicator.css';

export default function StatusIndicator({ status = 'idle', size = 'md' }) {
  const sizeClass = size === 'sm' ? 'size-sm' : size === 'lg' ? 'size-lg' : '';

  return (
    <span className="status-indicator">
      <span className={`status-dot ${status} ${sizeClass}`} />
      {(status === 'running' || status === 'error') && (
        <span className={`status-ring ${status} ${sizeClass}`} />
      )}
    </span>
  );
}
