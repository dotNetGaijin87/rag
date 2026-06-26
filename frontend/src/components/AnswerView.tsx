import { useState } from 'react';
import type { AnswerResponse } from '../api/types';

interface Props {
  result: AnswerResponse;
}

export function AnswerView({ result }: Props) {
  const [showSources, setShowSources] = useState(false);
  const { answer, context } = result;

  return (
    <div className="answer">
      <h3>Answer</h3>
      <p className="answer-text">{answer}</p>

      <button className="link-button" onClick={() => setShowSources((s) => !s)}>
        {showSources ? 'Hide' : 'Show'} sources ({context.chunks.length} passages,{' '}
        {context.facts.length} graph facts)
      </button>

      {showSources && (
        <div className="sources">
          {context.facts.length > 0 && (
            <div className="sources-block">
              <h4>Knowledge-graph facts</h4>
              <ul className="facts">
                {context.facts.map((fact, i) => (
                  <li key={i}>
                    <span className="entity">{fact.source}</span>
                    <span className="rel"> {fact.type.replace(/_/g, ' ').toLowerCase()} </span>
                    <span className="entity">{fact.target}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {context.chunks.length > 0 && (
            <div className="sources-block">
              <h4>Retrieved passages</h4>
              {context.chunks.map((chunk) => (
                <div key={chunk.chunk_id} className="chunk">
                  <div className="chunk-meta">
                    score {chunk.score.toFixed(3)}
                    {chunk.entities.length > 0 && (
                      <span className="chunk-entities">
                        {chunk.entities.map((e) => (
                          <span key={e} className="chip">
                            {e}
                          </span>
                        ))}
                      </span>
                    )}
                  </div>
                  <p className="chunk-text">{chunk.text}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
