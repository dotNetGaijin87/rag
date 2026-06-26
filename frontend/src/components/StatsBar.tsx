import type { Stats } from '../api/types';

interface Props {
  stats: Stats | null;
  onReset: () => void;
}

export function StatsBar({ stats, onReset }: Props) {
  return (
    <div className="stats-bar">
      <div className="stats-items">
        <Stat label="Documents" value={stats?.documents} />
        <Stat label="Chunks" value={stats?.chunks} />
        <Stat label="Entities" value={stats?.entities} />
        <Stat label="Relationships" value={stats?.relationships} />
      </div>
      <button className="link-button danger" onClick={onReset}>
        Reset knowledge base
      </button>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: number | undefined }) {
  return (
    <div className="stat">
      <span className="stat-value">{value ?? '—'}</span>
      <span className="stat-label">{label}</span>
    </div>
  );
}
