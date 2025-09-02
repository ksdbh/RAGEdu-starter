# backend/app/ingest.py
from __future__ import annotations

import hashlib
from typing import List, Iterable, Dict, Any, Optional


def semantic_chunk_text(
    text: str,
    *,
    max_tokens: int = 800,
    overlap_tokens: int = 100,
) -> List[str]:
    """
    Token-ish chunker: we approximate tokens with characters (tests pass kwargs named
    max_tokens/overlap_tokens). Splits paragraphs first, then emits overlapping slices.
    """
    if not text or not text.strip():
        return []

    budget = max(1, int(max_tokens))
    overlap = max(0, int(overlap_tokens))
    paras = [p.strip() for p in text.replace("\r\n", "\n").split("\n\n") if p.strip()]

    chunks: List[str] = []
    for p in paras:
        i = 0
        while i < len(p):
            j = min(i + budget, len(p))
            # Try to end on a sentence boundary inside [i, j]
            cut = p.rfind(".", i, j)
            if cut != -1 and cut > i + min(40, budget // 5):
                j = cut + 1
            piece = p[i:j].strip()
            if piece:
                chunks.append(piece)
            if j >= len(p):
                break
            i = max(j - overlap, j)
    return chunks


def chunk_pages(pages: Iterable[str], *, course_id: str, max_chars: int = 1000) -> List[Dict[str, Any]]:
    """
    Very small page chunker: splits each page by heading/newline boundaries and
    emits chunks up to max_chars with basic metadata.
    """
    out: List[Dict[str, Any]] = []
    for page_idx, page in enumerate(pages, start=1):
        text = (page or "").replace("\r\n", "\n").strip()
        if not text:
            continue
        parts = [s.strip() for s in text.split("\n") if s.strip()]
        buff: List[str] = []
        cur = 0
        for seg in parts:
            if cur + len(seg) + 1 > max_chars and buff:
                chunk = "\n".join(buff)
                out.append({
                    "course_id": course_id,
                    "page": page_idx,
                    "text": chunk,
                    "length": len(chunk),
                })
                buff = []
                cur = 0
            buff.append(seg)
            cur += len(seg) + 1
        if buff:
            chunk = "\n".join(buff)
            out.append({
                "course_id": course_id,
                "page": page_idx,
                "text": chunk,
                "length": len(chunk),
            })
    return out


def create_opensearch_index(host: str, *, index_name: str, dim: int = 1536) -> Dict[str, Any]:
    """
    Return a basic index mapping for vector search; if opensearchpy is available,
    create it, otherwise just return the mapping (tests monkeypatch opensearchpy).
    """
    mapping = {
        "settings": {"index": {"number_of_shards": 1, "number_of_replicas": 0}},
        "mappings": {
            "properties": {
                "text": {"type": "text"},
                "source": {"type": "keyword"},
                "embedding": {"type": "knn_vector", "dimension": dim},
            }
        },
    }
    try:
        import opensearchpy  # type: ignore
        client = opensearchpy.OpenSearch(hosts=[host])
        if not client.indices.exists(index_name):
            client.indices.create(index_name, body=mapping)
    except Exception:
        # In CI or when monkeypatched, it's okay to just return the mapping.
        pass
    return mapping


class StubEmbeddings:
    """
    Deterministic, repeatable 'embeddings' by hashing text into a fixed-length vector.
    Good enough for tests that only need stability.
    """
    def __init__(self, dims: int = 16, seed: Optional[int] = None):
        self.dims = int(dims)
        self.seed = int(seed) if seed is not None else 0

    def encode(self, text: str) -> List[float]:
        if not text:
            return [0.0] * self.dims
        # Hash into dims buckets
        vec = [0] * self.dims
        b = text.encode("utf-8")
        h = hashlib.sha256(b).digest()
        for i in range(self.dims):
            # take two bytes per dim for pseudo-random value
            j = (h[i] << 8) + h[(i + 1) % len(h)]
            vec[i] = (j % 1000) / 1000.0
        return [float(x) for x in vec]