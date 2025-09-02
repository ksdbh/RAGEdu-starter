# backend/app/rag.py
from __future__ import annotations

from typing import Any, Dict, List, Protocol, Sequence, TypedDict, Optional


# Guardrail sentinel expected by tests
GUARDRAIL_NEED_MORE_SOURCES = "NEED_MORE_SOURCES"


class OpenSearchClientInterface(Protocol):
    def index(self, index: str, document: Dict[str, Any]) -> Any: ...
    def search(self, index: str, body: Dict[str, Any]) -> Dict[str, Any]: ...


class LLMAdapterInterface(Protocol):
    def generate(self, prompt: str, *, system: Optional[str] = None) -> str: ...


class HitDoc(TypedDict, total=False):
    text: str
    source: str
    score: float


def build_knn_query(*, vector: Sequence[float], field: str = "embedding", k: int = 3) -> Dict[str, Any]:
    return {"size": k, "query": {"knn": {field: {"vector": list(vector), "k": k}}}}


def _normalize_hits(res: Dict[str, Any]) -> List[HitDoc]:
    out: List[HitDoc] = []
    for h in res.get("hits", {}).get("hits", []):
        src = h.get("_source", {}) or {}
        out.append(HitDoc(
            text=str(src.get("text", "")),
            source=str(src.get("source", "")),
            score=float(h.get("_score", 0.0)),
        ))
    return out


def retrieve(
    client: OpenSearchClientInterface,
    *,
    index: str,
    vector: Sequence[float],
    top_k: int = 3,
    field: str = "embedding",
) -> List[HitDoc]:
    body = build_knn_query(vector=vector, field=field, k=top_k)
    res = client.search(index=index, body=body)
    return _normalize_hits(res)


def generate_answer(
    llm: LLMAdapterInterface,
    *,
    question: str,
    contexts: Sequence[str],
    system: Optional[str] = "You are a helpful study assistant. Ground answers in provided context."
) -> str:
    ctx_block = "\n\n".join(f"- {c}" for c in contexts if c)
    prompt = (
        f"{system}\n\n"
        f"Question:\n{question}\n\n"
        f"Context:\n{ctx_block}\n\n"
        f"Answer clearly and concisely. Cite relevant snippets by index if needed."
    )
    return llm.generate(prompt, system=system)


def rag_answer(
    llm: LLMAdapterInterface,
    client: OpenSearchClientInterface,
    *,
    index: str,
    question: str,
    embedding: Sequence[float],
    top_k: int = 3,
    field: str = "embedding",
) -> Dict[str, Any]:
    hits = retrieve(client, index=index, vector=embedding, top_k=top_k, field=field)
    contexts = [h.get("text", "") for h in hits]
    answer = generate_answer(llm, question=question, contexts=contexts)
    citations = [h.get("source", "") for h in hits if h.get("source")]
    return {"answer": answer, "citations": citations}


# --- Test-oriented convenience API expected by backend/tests/test_rag.py ---

def answer_query(
    question: str,
    *,
    search_client: Any,
    llm_client: Any,
    top_k: int = 3,
    rerank: bool = True,
    min_similarity: float = 0.5,
) -> Dict[str, Any]:
    """
    Tests call this with a FakeSearchClient(docs) and FakeLLM().
    We call search_client.search(question, top_k=..., rerank=...) -> list[doc],
    where each doc has at least {snippet, score, title?, page?, id?, recency?, section_score?}.
    We compute a simple "top_sim" from doc['score'] and apply a guardrail:
      if top_sim < min_similarity -> return NEED_MORE_SOURCES.
    Otherwise, join snippets and ask the LLM for the answer.
    """
    docs: List[Dict[str, Any]] = list(search_client.search(question, top_k=top_k, rerank=rerank) or [])
    # Normalize scores to [0,1] if possible; assume incoming 0..1 already for tests.
    top_sim = max((float(d.get("score", 0.0)) for d in docs), default=0.0)
    if top_sim < float(min_similarity):
        return {"answer": GUARDRAIL_NEED_MORE_SOURCES, "citations": []}

    contexts = [str(d.get("snippet", "")) for d in docs if d.get("snippet")]
    answer = llm_client.generate(
        "Answer the user's question using only the context:\n\n"
        + "\n".join(f"- {c}" for c in contexts) +
        f"\n\nQuestion: {question}\n\nProvide a concise answer.",
    )
    citations = []
    for d in docs:
        title = d.get("title") or "Doc"
        page = d.get("page")
        if page is not None:
            citations.append(f"{title} p.{page}")
        else:
            citations.append(str(title))
    return {"answer": answer, "citations": citations}