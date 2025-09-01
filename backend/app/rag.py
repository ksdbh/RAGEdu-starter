from typing import List, Dict, Optional, Any


class OpenSearchClientInterface:
    """Minimal interface expected by the RAG retrieval logic.

    Implementations should return a list of document dicts from knn_query:
      [{
        'id': str,
        'title': str,
        'page': Optional[int],
        'snippet': str,
        'score': float,            # raw vector similarity / distance (higher = better)
        # optional signals used by lightweight reranker:
        'recency': Optional[float],
        'section_score': Optional[float],
      }, ...]
    """

    def knn_query(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        raise NotImplementedError()


class LLMAdapterInterface:
    """Minimal LLM adapter interface used by the RAG logic.

    Implementations should provide generate(prompt) -> { 'text': str, 'confidence': Optional[float] }
    """

    def generate(self, prompt: str) -> Dict[str, Any]:
        raise NotImplementedError()


GUARDRAIL_NEED_MORE_SOURCES = "I don't have enough reliable sources to answer that question. Please provide more materials or try rephrasing."


def _normalize_scores(docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Normalize raw score values to [0,1] by dividing by max (preserve order)
    if not docs:
        return docs
    max_score = max((d.get("score", 0.0) for d in docs), default=0.0)
    if max_score and max_score > 0:
        for d in docs:
            d["_sim"] = float(d.get("score", 0.0)) / float(max_score)
    else:
        # fallback: if all scores are zero/negative, map linearly into 0..1 using min/max
        min_score = min((d.get("score", 0.0) for d in docs), default=0.0)
        denom = (max_score - min_score) if (max_score - min_score) != 0 else 1.0
        for d in docs:
            d["_sim"] = (float(d.get("score", 0.0)) - min_score) / denom
    return docs


def _rerank_by_recency_section(docs: List[Dict[str, Any]], recency_weight: float = 0.2, section_weight: float = 0.1) -> List[Dict[str, Any]]:
    """Apply a lightweight rerank that boosts documents by recency and section_score.

    Uses normalized similarity (d["_sim"]) produced by _normalize_scores.
    recency is expected to be a number (e.g. epoch or relative days) where higher is newer.
    section_score is expected in [0,1].
    """
    if not docs:
        return docs

    # normalize recency to [0,1] if present
    recencies = [d.get("recency") for d in docs if d.get("recency") is not None]
    if recencies:
        max_rec = max(recencies)
        min_rec = min(recencies)
        denom = (max_rec - min_rec) if (max_rec - min_rec) != 0 else 1.0
        for d in docs:
            r = d.get("recency")
            d["_recency_norm"] = (float(r) - min_rec) / denom if r is not None else 0.0
    else:
        for d in docs:
            d["_recency_norm"] = 0.0

    for d in docs:
        section_score = float(d.get("section_score", 0.0))
        sim = float(d.get("_sim", 0.0))
        recency_norm = float(d.get("_recency_norm", 0.0))
        # Compose final score: prefer similarity but add small boosts
        d["_final_score"] = (1.0 - recency_weight - section_weight) * sim + recency_weight * recency_norm + section_weight * section_score

    # sort descending by final score
    docs.sort(key=lambda x: x.get("_final_score", 0.0), reverse=True)
    return docs


def _format_citation(d: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "title": d.get("title") or "",
        "page": d.get("page"),
        "snippet": d.get("snippet") or "",
        "score": round(float(d.get("_final_score", d.get("_sim", 0.0))), 4),
    }


def _build_prompt(query: str, citations: List[Dict[str, Any]]) -> str:
    """Build a prompt that explicitly REQUIRES citations in the answer.

    The template instructs the LLM to include inline citations for each claim using
    the format [Title, page X] and to not hallucinate sources. The caller may
    enforce guardrails before calling the LLM.
    """
    src_texts = []
    for i, c in enumerate(citations, start=1):
        title = c.get("title", "source")
        page = c.get("page")
        snippet = c.get("snippet", "")
        if page is not None:
            src_texts.append(f"[{i}] {title} (page {page}): {snippet}")
        else:
            src_texts.append(f"[{i}] {title}: {snippet}")

    prompt = (
        "You are an assistant answering a question based ONLY on the provided sources below. "
        "Cite any factual claims inline using the bracketed source index and title (e.g. [1] Title, page 3). "
        "If the sources do not contain enough information to answer, respond with: 'I don't have enough reliable sources to answer that question.'\n\n"
        "Sources:\n"
        f"{chr(10).join(src_texts)}\n\n"
        "Question: "
        f"{query}\n\n"
        "Answer (include citations):"
    )
    return prompt


def answer_query(
    query: str,
    search_client: OpenSearchClientInterface,
    llm_client: LLMAdapterInterface,
    top_k: int = 5,
    rerank: bool = False,
    min_similarity: float = 0.65,
) -> Dict[str, Any]:
    """Main retrieval + answer flow used by the API.

    - Calls search_client.knn_query(query, top_k) to fetch nearest neighbors.
    - Normalizes scores and optionally reranks by recency/section_score.
    - If the top similarity is below min_similarity a guardrail response is returned
      (no LLM call) asking for more sources.
    - Otherwise, builds a citation-aware prompt and calls llm_client.generate(prompt).

    Returns:
      { answer: str, citations: [{title,page,snippet,score}], confidence: float }
    """
    if not query or not query.strip():
        return {"answer": "", "citations": [], "confidence": 0.0}

    # fetch KNN candidates from OpenSearch (adapter responsibility to compute/query embeddings)
    docs = search_client.knn_query(query=query, top_k=top_k)
    if not docs:
        return {"answer": GUARDRAIL_NEED_MORE_SOURCES, "citations": [], "confidence": 0.0}

    # normalize scores
    _normalize_scores(docs)

    # apply rerank if requested
    if rerank:
        _rerank_by_recency_section(docs)
    else:
        # set final score equal to normalized similarity for later use
        for d in docs:
            d["_final_score"] = d.get("_sim", 0.0)

    # check guardrail: require top candidate similarity above threshold
    top_sim = docs[0].get("_sim", 0.0)
    if top_sim < float(min_similarity):
        return {"answer": GUARDRAIL_NEED_MORE_SOURCES, "citations": [], "confidence": 0.0}

    # prepare citations for the prompt (we pass top_k docs)
    citations_for_prompt = docs[:top_k]
    prompt = _build_prompt(query=query, citations=citations_for_prompt)

    # call the LLM with the prompt
    llm_res = llm_client.generate(prompt)
    text = llm_res.get("text") or ""
    conf = float(llm_res.get("confidence", 0.0)) if llm_res.get("confidence") is not None else 0.0

    # package citations in response, exposing title/page/snippet/score
    citations_out = [_format_citation(d) for d in citations_for_prompt]

    return {"answer": text, "citations": citations_out, "confidence": round(conf, 4)}
