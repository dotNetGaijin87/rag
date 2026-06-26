"""Domain models — plain dataclasses with no framework or infrastructure dependencies.

These are the core concepts of the RAG system. They are deliberately free of any
Neo4j / Flask / Ollama imports so the domain stays independent of the outside world.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class Chunk:
    """A contiguous slice of a document that is embedded and stored in the graph."""

    id: str
    document_id: str
    index: int
    text: str
    embedding: Optional[list[float]] = None


@dataclass(frozen=True)
class Entity:
    """A semantic entity (person, organisation, concept, ...) extracted from text."""

    name: str
    type: str = "Concept"
    description: str = ""


@dataclass(frozen=True)
class Relationship:
    """A directed, semantic relationship between two entities."""

    source: str
    target: str
    type: str = "RELATED_TO"
    description: str = ""


@dataclass(frozen=True)
class ExtractionResult:
    """Output of LLM knowledge-graph extraction over a piece of text."""

    entities: list[Entity] = field(default_factory=list)
    relationships: list[Relationship] = field(default_factory=list)


@dataclass(frozen=True)
class Document:
    """A unit of text ingested by the user."""

    id: str
    title: str
    text: str
    chunks: list[Chunk] = field(default_factory=list)


@dataclass(frozen=True)
class RetrievedChunk:
    """A chunk returned from retrieval, enriched with graph context."""

    chunk_id: str
    document_id: str
    text: str
    score: float
    entities: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class GraphFact:
    """A (source)-[type]->(target) fact assembled from the graph for the LLM."""

    source: str
    type: str
    target: str
    description: str = ""

    def as_sentence(self) -> str:
        rel = self.type.replace("_", " ").lower()
        base = f"{self.source} {rel} {self.target}"
        return f"{base} ({self.description})" if self.description else base


@dataclass(frozen=True)
class RetrievalContext:
    """Everything retrieval assembled to ground the answer."""

    chunks: list[RetrievedChunk] = field(default_factory=list)
    facts: list[GraphFact] = field(default_factory=list)


@dataclass(frozen=True)
class Answer:
    """The final grounded answer plus the evidence used to produce it."""

    question: str
    answer: str
    context: RetrievalContext


@dataclass(frozen=True)
class IngestionReport:
    """Summary of what an ingestion produced — returned to the UI."""

    document_id: str
    title: str
    chunk_count: int
    entity_count: int
    relationship_count: int
