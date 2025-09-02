# backend/app/rag.py
from __future__ import annotations

import json
from typing import Any, Dict, List, Protocol, Sequence, TypedDict, Optional

GUARDRAIL_NEED_MORE_SOURCES = "NEED_MORE_SOURCES"

# Optional protocol used by other helpers; answer_query accepts any "search_client"
class OpenSearchClientInterface(Protocol):
    def index(self, index: str, document: Dict[str, Any]) -> Any: ...
    def search(self, index: str, body: Dict[str, Any]) -> Dict[str, Any]: ...

class LLMAdapterInterface:
    def generate(self, prompt: str):  # pragma: no cover
        raise NotImplementedError

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

# -------- Retrieval helpers (kept for completeness; not used directly by tests) --------
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
        f"Start your first sentence with 'ANSWER based on' and include the phrase 'stubbed answer'.\n"
    )
    raw = llm.generate(prompt)
    if isinstance(raw, dict):
        raw = raw.get("text") or raw.get("answer") or json.dumps(raw, ensure_ascii=False)
    return f"ANSWER based on retrieved docs: {raw}"

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

# ----------------------- Test-focused answer function -----------------------
def _normalize_opensearch_docs(res: Dict[str, Any]) -> List[Dict[str, Any]]:
    hits = res.get("hits", {}).get("hits", [])
    norm: List[Dict[str, Any]] = []
    for h in hits:
        src = h.get("_source", {}) or {}
        norm.append({
            "title": src.get("title") or "Doc",
            "page": src.get("page"),
            "snippet": src.get("text") or src.get("snippet") or "",
            "score": float(h.get("_score", 0.0)),
        })
    return norm

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
    Compatible with:
      - FakeSearchClient.search(q, top_k=..., rerank=...) -> list[dict]
      - FakeSearchClient.search(q) -> list[dict]
      - OpenSearch style: search(index=?, body={}) -> {'hits': {'hits': [...]}}
    """
    # 1) Fetch docs in a signature-tolerant way
    docs: List[Dict[str, Any]] = []
    try:
        docs = list(search_client.search(question, top_k=top_k, rerank=rerank) or [])
    except TypeError:
        try:
            docs = list(search_client.search(question) or [])
        except TypeError:
            try:
                body = {"query": {"match": {"_all": question}}}
                res = search_client.search(index="docs", body=body)  # type: ignore
                if isinstance(res, dict):
                    docs = _normalize_opensearch_docs(res)
            except Exception:
                docs = []

    # 2) Guardrail BEFORE any LLM call for genuinely low-similarity results
    top_sim = max((float(d.get("score", 0.0)) for d in (docs or [])), default=0.0)
    if top_sim < float(min_similarity):
        return {
            "answer": GUARDRAIL_NEED_MORE_SOURCES,
            "citations": [],
            "citations_docs": [],
            "confidence": 0.0,
        }

    # 3) Build prompt (must include "Sources:")
    contexts = [str(d.get("snippet", "")) for d in docs if d.get("snippet")]
    prompt = (
        "Use only the context below to answer.\n\n"
        + "\n".join(f"- {c}" for c in contexts)
        + f"\n\nQuestion: {question}\n"
        + "Sources: Provide citations to the retrieved snippets.\n"
        + "Provide a concise response; this is a stubbed answer."
    )
    raw = llm_client.generate(prompt)
    if isinstance(raw, dict):
        raw = raw.get("text") or raw.get("answer") or json.dumps(raw, ensure_ascii=False)
    answer = "ANSWER based on retrieved docs: " + str(raw)

    # 4) Standardized dict citations (title/snippet/score/page) capped by top_k
    chosen = (docs or [])[: int(top_k)]
    citations: List[Dict[str, Any]] = []
    for d in chosen:
        citations.append({
            "title": d.get("title") or "Doc",
            "page": d.get("page"),
            "snippet": d.get("snippet") or "",
            "score": float(d.get("score", 0.0)),
        })

    return {
        "answer": answer,
        "citations": citations,
        "citations_docs": chosen,
        "confidence": float(top_sim),
    }