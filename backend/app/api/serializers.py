"""Translate domain objects into JSON-serialisable dicts for the HTTP layer."""

from __future__ import annotations

from ..domain.models import Answer, IngestionReport, RetrievedChunk


def serialize_report(report: IngestionReport) -> dict:
    return {
        "document_id": report.document_id,
        "title": report.title,
        "chunk_count": report.chunk_count,
        "entity_count": report.entity_count,
        "relationship_count": report.relationship_count,
    }


def _serialize_chunk(chunk: RetrievedChunk) -> dict:
    return {
        "chunk_id": chunk.chunk_id,
        "document_id": chunk.document_id,
        "text": chunk.text,
        "score": round(chunk.score, 4),
        "entities": chunk.entities,
    }


def serialize_answer(answer: Answer) -> dict:
    return {
        "question": answer.question,
        "answer": answer.answer,
        "context": {
            "chunks": [_serialize_chunk(c) for c in answer.context.chunks],
            "facts": [
                {
                    "source": f.source,
                    "type": f.type,
                    "target": f.target,
                    "description": f.description,
                    "sentence": f.as_sentence(),
                }
                for f in answer.context.facts
            ],
        },
    }
