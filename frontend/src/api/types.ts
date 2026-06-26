// Shapes mirror the backend's JSON serializers.

export interface IngestionReport {
  document_id: string;
  title: string;
  chunk_count: number;
  entity_count: number;
  relationship_count: number;
}

export interface RetrievedChunk {
  chunk_id: string;
  document_id: string;
  text: string;
  score: number;
  entities: string[];
}

export interface GraphFact {
  source: string;
  type: string;
  target: string;
  description: string;
  sentence: string;
}

export interface AnswerResponse {
  question: string;
  answer: string;
  context: {
    chunks: RetrievedChunk[];
    facts: GraphFact[];
  };
}

export interface Stats {
  documents: number;
  chunks: number;
  entities: number;
  relationships: number;
}
