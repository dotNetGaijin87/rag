"""Unit tests for the question-answering use case."""

import pytest

from app.application.answer_question import AnswerQuestionUseCase, _parse_rank_order
from app.config import Config
from app.domain.models import ExtractionResult, GraphFact, RetrievedChunk
from app.domain.ports import LLMProvider
from app.settings import RuntimeSettings

from tests.conftest import FakeEmbeddingProvider, FakeGraphRepository, FakeLLMProvider


def _chunks(*ids):
    return [
        RetrievedChunk(chunk_id=i, document_id="d", text=f"text {i}", score=0.5, entities=[])
        for i in ids
    ]


def _make_uc(llm, top_k=5, overfetch=4, graph=None):
    settings = RuntimeSettings(Config())
    settings.top_k = top_k
    return AnswerQuestionUseCase(
        embeddings=FakeEmbeddingProvider(),
        llm=llm,
        graph=graph or FakeGraphRepository(),
        settings=settings,
        rerank_overfetch=overfetch,
    )


@pytest.mark.parametrize("blank", ["", "   ", None])
def test_empty_question_is_rejected(answer_uc, blank):
    with pytest.raises(ValueError):
        answer_uc.execute(question=blank)


def test_answers_from_retrieved_context(answer_uc, llm, graph):
    answer = answer_uc.execute(question="What did Curie discover?")

    assert answer.answer == "Marie Curie discovered radium."
    assert answer.question == "What did Curie discover?"
    assert len(answer.context.chunks) == 1
    assert len(answer.context.facts) == 1
    assert graph.facts_calls[-1]["names"] == ["Marie Curie"]


def test_returns_canned_reply_and_skips_llm_when_nothing_is_found():
    graph = FakeGraphRepository(chunks=[], facts=[])
    llm = FakeLLMProvider()
    use_case = AnswerQuestionUseCase(
        embeddings=FakeEmbeddingProvider(),
        llm=llm,
        graph=graph,
        settings=RuntimeSettings(Config()),
    )

    answer = use_case.execute(question="Something unknown?")

    assert "don't have any information" in answer.answer
    assert answer.context.chunks == []
    assert llm.generate_calls == []


def test_chunks_without_entities_skip_the_graph_fact_lookup():
    chunk = RetrievedChunk(
        chunk_id="doc-0", document_id="doc", text="Some text.", score=0.5, entities=[]
    )
    graph = FakeGraphRepository(chunks=[chunk], facts=[GraphFact("X", "Y", "Z")])
    use_case = AnswerQuestionUseCase(
        embeddings=FakeEmbeddingProvider(),
        llm=FakeLLMProvider(),
        graph=graph,
        settings=RuntimeSettings(Config()),
    )

    answer = use_case.execute(question="Anything?")

    assert answer.context.facts == []
    assert graph.facts_calls == []


def test_query_matched_entities_broaden_the_fact_lookup():
    # Default chunk mentions "Marie Curie"; entity vector search adds "Pierre Curie".
    graph = FakeGraphRepository(seed_entities=["Pierre Curie"])
    use_case = AnswerQuestionUseCase(
        embeddings=FakeEmbeddingProvider(),
        llm=FakeLLMProvider(),
        graph=graph,
        settings=RuntimeSettings(Config()),
    )

    use_case.execute(question="Who did Curie work with?")

    assert graph.facts_calls[-1]["names"] == ["Marie Curie", "Pierre Curie"]
    assert graph.entity_search_calls[-1]["k"] == 5


def test_graph_can_answer_when_chunk_search_returns_nothing():
    graph = FakeGraphRepository(chunks=[], seed_entities=["Marie Curie"])
    llm = FakeLLMProvider()
    use_case = AnswerQuestionUseCase(
        embeddings=FakeEmbeddingProvider(),
        llm=llm,
        graph=graph,
        settings=RuntimeSettings(Config()),
    )

    answer = use_case.execute(question="What did Curie discover?")

    assert answer.context.chunks == []
    assert len(answer.context.facts) == 1
    assert answer.answer == "Marie Curie discovered radium."
    assert llm.generate_calls


def test_retrieval_uses_top_k_from_settings(graph):
    settings = RuntimeSettings(Config())
    settings.top_k = 9
    settings.enable_reranking = False  # plain top_k retrieval (no over-fetch)
    use_case = AnswerQuestionUseCase(
        embeddings=FakeEmbeddingProvider(),
        llm=FakeLLMProvider(),
        graph=graph,
        settings=settings,
    )

    use_case.execute(question="What did Curie discover?")

    assert graph.search_calls[-1]["k"] == 9


def test_parse_rank_order_dedupes_and_ignores_out_of_range():
    assert _parse_rank_order("3, 1, 1, 9, 2", 3) == [2, 0, 1]


def test_rerank_reorders_chunks_by_llm_ranking():
    use_case = _make_uc(FakeLLMProvider(answer="3, 1, 2"), top_k=3)

    out = use_case._rerank("q", _chunks("a", "b", "c", "d"))

    assert [c.chunk_id for c in out] == ["c", "a", "b"]


def test_rerank_appends_chunks_the_llm_omitted():
    use_case = _make_uc(FakeLLMProvider(answer="2"), top_k=3)

    out = use_case._rerank("q", _chunks("a", "b", "c", "d"))

    assert [c.chunk_id for c in out] == ["b", "a", "c"]


def test_rerank_falls_back_to_retrieval_order_when_unparseable():
    use_case = _make_uc(FakeLLMProvider(answer="no numbers here"), top_k=2)

    out = use_case._rerank("q", _chunks("a", "b", "c"))

    assert [c.chunk_id for c in out] == ["a", "b"]


def test_rerank_is_skipped_when_candidates_already_fit():
    llm = FakeLLMProvider()
    use_case = _make_uc(llm, top_k=5)

    out = use_case._rerank("q", _chunks("a", "b"))

    assert [c.chunk_id for c in out] == ["a", "b"]
    assert llm.generate_calls == []  # no LLM call when there is nothing to rerank


def test_rerank_falls_back_when_the_llm_errors():
    class _BoomLLM(LLMProvider):
        def generate(self, system, prompt):
            raise RuntimeError("boom")

        def extract_graph(self, text):
            return ExtractionResult()

    use_case = _make_uc(_BoomLLM(), top_k=2)

    out = use_case._rerank("q", _chunks("a", "b", "c"))

    assert [c.chunk_id for c in out] == ["a", "b"]


def test_execute_overfetches_then_reranks():
    graph = FakeGraphRepository(chunks=_chunks("a", "b", "c", "d", "e", "f"))
    use_case = _make_uc(FakeLLMProvider(answer="2, 1"), top_k=2, overfetch=4, graph=graph)

    answer = use_case.execute(question="q")

    assert graph.search_calls[-1]["k"] == 8  # top_k (2) * overfetch (4)
    assert [c.chunk_id for c in answer.context.chunks] == ["b", "a"]
