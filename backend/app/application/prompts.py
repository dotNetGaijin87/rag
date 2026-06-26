"""Prompt templates for extraction and answering.

Kept in the application layer because they encode RAG behaviour, not infrastructure.
"""

from __future__ import annotations

from ..domain.models import RetrievalContext

# --------------------------------------------------------------------------- #
# Knowledge-graph extraction
# --------------------------------------------------------------------------- #

EXTRACTION_SYSTEM = (
    "You are an expert at building knowledge graphs from text. "
    "You extract the key entities and the relationships between them. "
    "Respond with strict JSON only — no prose, no markdown."
)

EXTRACTION_PROMPT_TEMPLATE = """\
Extract a knowledge graph from the text below.

Return JSON with exactly this shape:
{{
  "entities": [
    {{"name": "<canonical name>", "type": "<Person|Organization|Location|Concept|Product|Event|Other>", "description": "<short description>"}}
  ],
  "relationships": [
    {{"source": "<entity name>", "target": "<entity name>", "type": "<UPPER_SNAKE_CASE verb>", "description": "<short description>"}}
  ]
}}

Rules:
- Use concise, canonical entity names (e.g. "Marie Curie", not "she").
- Every relationship's source and target MUST appear in the entities list.
- Prefer 5-20 of the most important entities; do not invent facts.
- If nothing meaningful can be extracted, return empty lists.

Text:
\"\"\"
{text}
\"\"\"
"""


def extraction_prompt(text: str) -> str:
    return EXTRACTION_PROMPT_TEMPLATE.format(text=text)


# --------------------------------------------------------------------------- #
# Answering
# --------------------------------------------------------------------------- #

ANSWER_SYSTEM = (
    "You are a helpful assistant that answers questions using ONLY the provided "
    "context, which comes from the user's own knowledge base. "
    "If the context does not contain the answer, say you don't have enough "
    "information. Be concise and factual. Do not invent details."
)

ANSWER_PROMPT_TEMPLATE = """\
Answer the question using only the context below.

# Knowledge graph facts
{facts}

# Retrieved passages
{passages}

# Question
{question}

# Answer
"""


def answer_prompt(question: str, context: RetrievalContext) -> str:
    if context.facts:
        facts = "\n".join(f"- {fact.as_sentence()}" for fact in context.facts)
    else:
        facts = "(none)"

    if context.chunks:
        passages = "\n\n".join(
            f"[Passage {i + 1}] {chunk.text}" for i, chunk in enumerate(context.chunks)
        )
    else:
        passages = "(none)"

    return ANSWER_PROMPT_TEMPLATE.format(facts=facts, passages=passages, question=question)
