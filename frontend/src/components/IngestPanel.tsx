import { useState, type FormEvent } from 'react';
import { api, ApiError } from '../api/client';
import type { IngestionReport } from '../api/types';

interface Props {
  onIngested: () => void;
}

export function IngestPanel({ onIngested }: Props) {
  const [title, setTitle] = useState('');
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [report, setReport] = useState<IngestionReport | null>(null);

  const canSubmit = text.trim().length > 0 && !loading;

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!canSubmit) return;

    setLoading(true);
    setError(null);
    setReport(null);
    try {
      const result = await api.ingest(text.trim(), title.trim());
      setReport(result);
      setText('');
      setTitle('');
      onIngested();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Something went wrong.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="panel">
      <h2>1 · Add knowledge</h2>
      <p className="panel-hint">
        Paste any text. It is chunked, embedded, and an entity/relationship graph is
        extracted and stored in Neo4j.
      </p>
      <form onSubmit={handleSubmit} className="stack">
        <input
          type="text"
          placeholder="Title (optional)"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          disabled={loading}
        />
        <textarea
          placeholder="Paste text to remember…"
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={10}
          disabled={loading}
        />
        <button type="submit" disabled={!canSubmit}>
          {loading ? 'Ingesting…' : 'Add to knowledge base'}
        </button>
      </form>

      {error && <p className="message error">{error}</p>}
      {report && (
        <p className="message success">
          Stored “{report.title}” — {report.chunk_count} chunks, {report.entity_count}{' '}
          entities, {report.relationship_count} relationships.
        </p>
      )}
    </section>
  );
}
