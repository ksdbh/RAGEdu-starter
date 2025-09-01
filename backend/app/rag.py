import math
import time
from typing import Any, Dict, List, Optional, Tuple

from .ingest import BedrockEmbeddingClientStub


class OpenSearchRetrieverStub:
    """A lightweight in-memory retriever that mimics OpenSearch KNN behaviour.

    The corpus is deterministic and small so unit tests remain stable.
    Each document has: id, title, page, text, published_ts, section_score, embedding.
    """

    def __init__(self):
        self.embedder = BedrockEmbeddingClientStub()
        # Fixed "now" so recency calculations are deterministic in tests
        self._now = 1_700_000_000
        # Build a tiny deterministic corpus
        base_texts = [
            ("Intro to Graphs", 1, "Graphs are collections of nodes and edges. This section covers basic terminology.", 1_699_999_900, 0.6),
            ("Shortest Paths", 12, "Dijkstra's algorithm finds shortest paths from a source in O(E + V log V) with a priority queue.", 1_699_999_800, 0.9),
            ("Heuristics and A*", 27, "A* uses heuristics to guide search, often faster than Dijkstra when heuristics are admissible.", 1_699_999_950, 0.95),
            ("Big-O Review", 45, "We briefly review algorithm complexity: constant, logarithmic, linear, polynomial, exponential.", 1_699_999_700, 0.4),
            ("Practice Problems", 99, "Worked examples comparing Dijkstra and A* on grid maps. Step-by-step trace provided.", 1_699_999_970, 0.85),
            ("Appendix", 120, "Reference tables and further reading links.", 1_699_999_600, 0.2),
        ]
        self.docs: List[Dict[str, Any]] = []
        for i, (title, page, text, ts, section_score) in enumerate(base_texts):
            doc = {
                "id": f"doc_{i}",
                "title": title,
                "page": page,
                "text": text,
                "published_ts": ts,
                "section_score": section_score,
            }
            # compute embedding
            emb = self.embedder.embed_texts([text])[0]
            doc["embedding"] = emb
            self.docs.append(doc)

    @staticmethod
    def _cosine(a: List[float], b: List[float]) -> float:
        # Defensive cosine similarity
        num = 0.0
        sa = 0.0
        sb = 0.0
        for x, y in zip(a, b):
            num += x * y
            sa += x * x
            sb += y * y
        if sa == 0 or sb == 0:
            return 0.0
        return num / (math.sqrt(sa) * math.sqrt(sb))

    def knn_search(self, query: str, top_k: int = 5, course_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return top_k candidate docs with a similarity score field ('sim')."""
        q_emb = self.embedder.embed_texts([query])[0]
        scored: List[Tuple[Dict[str, Any], float]] = []
        for d in self.docs:
            sim = self._cosine(q_emb, d["embedding"])
            scored.append((d.copy(), sim))
        # attach sim
        scored_docs = []
        for d, sim in scored:
            d["sim"] = sim
            scored_docs.append(d)
        # return top_k by sim
        scored_docs.sort(key=lambda x: x["sim"], reverse=True)
        return scored_docs[:top_k]

    def rerank_by_recency_and_section(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Re-rank candidate docs by combining similarity, recency and section_score.

        Score composition (weights chosen for deterministic behavior):
        final = 0.6 * sim + 0.3 * section_score + 0.1 * recency_score
        where recency_score is 1 - normalized_age (newer docs -> higher recency_score).
        """
        # For deterministic normalization, compute ages relative to self._now
        ages = [max(0, self._now - d.get("published_ts", 0)) for d in candidates]
        max_age = max(ages) if ages else 1
        reranked: List[Dict[str, Any]] = []
        for d, age in zip(candidates, ages):
            # recency_score: newer -> higher, map age 0 -> 1.0, max_age -> 0.0
            recency_score = 1.0 - (age / max_age) if max_age > 0 else 0.0
            sim = d.get("sim", 0.0)
            section = d.get("section_score", 0.0)
            final = 0.6 * sim + 0.3 * section + 0.1 * recency_score
            d = d.copy()
            d["recency_score"] = recency_score
            d["final_score"] = final
            reranked.append(d)
        reranked.sort(key=lambda x: x["final_score"], reverse=True)
        return reranked


class BedrockLLMClientStub:
    """Stub for Bedrock LLM generation.

    generate_answer returns a short synthesized answer that references the provided
    context snippets and a confidence score derived from final_scores.
    """

    def generate_answer(self, query: str, context_docs: List[Dict[str, Any]]) -> Tuple[str, float]:
        if not context_docs:
            return ("I don't have enough context to answer that question.", 0.0)

        # Pick the top snippets (first 3) and synthesize a short answer by concatenation
        parts: List[str] = []
        for d in context_docs[:3]:
            parts.append(f"From {d.get('title')} (page {d.get('page')}): {d.get('text')}")
        answer = f"Summary answer to: {query}\n\n" + "\n\n".join(parts)

        # Compute confidence as normalized average of final_score (final_score typically in [-1,1])
        scores = [d.get("final_score", 0.0) for d in context_docs]
        # Clamp and map to [0,1] for readability
        avg = sum(scores) / len(scores)
        # final_score can be small; map roughly from [-1,1] to [0,1]
        confidence = max(0.0, min(1.0, (avg + 1) / 2))
        return (answer, confidence)


def compose_citations(docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for d in docs:
        snippet = d.get("text", "")
        # snippet shorten
        if len(snippet) > 200:
            snippet = snippet[:197] + "..."
        out.append({"title": d.get("title"), "page": d.get("page"), "snippet": snippet})
    return out
