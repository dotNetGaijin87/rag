import { useCallback, useEffect, useState } from 'react';
import { api } from './api/client';
import type { Stats } from './api/types';
import { IngestPanel } from './components/IngestPanel';
import { QueryPanel } from './components/QueryPanel';
import { StatsBar } from './components/StatsBar';

export default function App() {
  const [stats, setStats] = useState<Stats | null>(null);

  const refreshStats = useCallback(() => {
    api
      .stats()
      .then(setStats)
      .catch(() => setStats(null));
  }, []);

  useEffect(() => {
    refreshStats();
  }, [refreshStats]);

  async function handleReset() {
    if (!window.confirm('Delete all stored knowledge?')) return;
    await api.reset().catch(() => undefined);
    refreshStats();
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>GraphRAG Knowledge Base</h1>
        <p className="subtitle">
          Local Retrieval-Augmented Generation · Neo4j · Ollama — fully offline
        </p>
      </header>

      <StatsBar stats={stats} onReset={handleReset} />

      <main className="grid">
        <IngestPanel onIngested={refreshStats} />
        <QueryPanel />
      </main>

      <footer className="app-footer">
        Paste text on the left, ask questions on the right. Nothing leaves your machine.
      </footer>
    </div>
  );
}
