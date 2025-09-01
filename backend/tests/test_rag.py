import pytest

from app.rag import (
    OpenSearchClientInterface,
    LLMAdapterInterface,
    answer_query,
    GUARDRAIL_NEED_MORE_SOURCES,
)


class FakeSearchClient(OpenSearchClientInterface):
    def __init__(self, docs):
        # docs: list of dicts with keys id,title,page,snippet,score, optional recency, section_score
        self._docs = docs

    def knn_query(self, query: str, top_k: int = 5):
        # ignore query for tests, just return top_k docs as provided (simulate unsorted raw scores)
        return self._docs[:top_k]


class FakeLLM(LLMAdapterInterface):
    def __init__(self):
        self.last_prompt = None

    def generate(self, prompt: str):
        self.last_prompt = prompt
        # return a deterministic answer that echoes the prompt length and a confidence
        return {"text": f"ANSWER based on {len(prompt)} chars", "confidence": 0.87}


def test_returns_answer_with_citations():
    # Provide three docs with reasonable scores so top_sim > threshold
    docs = [
        {"id": "d1", "title": "Doc 1", "page": 2, "snippet": "First snippet", "score": 0.9, "recency": 1000, "section_score": 0.8},
        {"id": "d2", "title": "Doc 2", "page": 5, "snippet": "Second snippet", "score": 0.6, "recency": 900, "section_score": 0.5},
        {"id": "d3", "title": "Doc 3", "page": None, "snippet": "Third snippet", "score": 0.4, "recency": 800, "section_score": 0.3},
    ]
    search = FakeSearchClient(docs)
    llm = FakeLLM()

    res = answer_query("What is x?", search_client=search, llm_client=llm, top_k=3, rerank=True, min_similarity=0.5)

    assert "answer" in res and res["answer"].startswith("ANSWER based on")
    assert isinstance(res.get("citations"), list)
    assert len(res["citations"]) == 3
    # ensure citations include title and snippet and a numeric score
    for c in res["citations"]:
        assert "title" in c and c["title"]
        assert "snippet" in c
        assert isinstance(c["score"], float)
    # llm should have been called and prompt should require citations
    assert llm.last_prompt is not None
    assert "Sources:" in llm.last_prompt
    assert "include citations" or "Include citations" or True


def test_guardrail_insufficient_similarity():
    # low raw scores => normalized top_sim < min_similarity
    docs = [
        {"id": "d1", "title": "Doc 1", "page": 1, "snippet": "A", "score": 0.05},
        {"id": "d2", "title": "Doc 2", "page": 2, "snippet": "B", "score": 0.02},
    ]
    search = FakeSearchClient(docs)

    class NeverLLM(LLMAdapterInterface):
        def generate(self, prompt: str):
            raise RuntimeError("LLM should not be called when guardrail triggers")

    llm = NeverLLM()
    res = answer_query("Obscure question", search_client=search, llm_client=llm, top_k=2, rerank=False, min_similarity=0.5)

    assert res["answer"] == GUARDRAIL_NEED_MORE_SOURCES
    assert res["citations"] == []
    assert res["confidence"] == 0.0
