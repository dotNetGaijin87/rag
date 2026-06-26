import { useState, type FormEvent } from 'react';
import { api, ApiError } from '../api/client';
import type { AnswerResponse } from '../api/types';
import { AnswerView } from './AnswerView';

export function QueryPanel() {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AnswerResponse | null>(null);

  const canSubmit = question.trim().length > 0 && !loading;

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!canSubmit) return;

    setLoading(true);
    setError(null);
    try {
      const response = await api.ask(question.trim());
      setResult(response);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Something went wrong.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="panel">
      <h2>2 · Ask a question</h2>
      <p className="panel-hint">
        Your question is embedded, matched against stored chunks, expanded over the graph,
        and answered by the local LLM — grounded only in what you added.
      </p>
      <form onSubmit={handleSubmit} className="stack">
        <textarea
          placeholder="Ask something about the text you added…"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          rows={3}
          disabled={loading}
        />
        <button type="submit" disabled={!canSubmit}>
          {loading ? 'Thinking…' : 'Ask'}
        </button>
      </form>

      {error && <p className="message error">{error}</p>}
      {result && <AnswerView result={result} />}
    </section>
  );
}
