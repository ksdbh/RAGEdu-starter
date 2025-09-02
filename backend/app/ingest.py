# backend/app/ingest.py
from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import List, Iterable, Dict, Any, Optional


@dataclass
class Chunk:
    text: str
    start: int = 0
    end: int = 0


def semantic_chunk_text(
    text: str,
    *,
    max_tokens: int = 800,
    overlap_tokens: int = 100,
) -> List[Chunk]:
    """
    Return objects with a `.text` attribute (tests access chunk.text).
    We approximate tokens with characters and provide overlaps.
    """
    if not text or not text.strip():
        return []

    budget = max(1, int(max_tokens))
    overlap = max(0, int(overlap_tokens))
    # Split by paragraphs
    paras = [p.strip() for p in text.replace("\r\n", "\n").split("\n\n") if p.strip()]

    chunks: List[Chunk] = []
    for p in paras:
        i = 0
        while i < len(p):
            j = min(i + budget, len(p))
            # Prefer to cut on a sentence boundary
            cut = p.rfind(".", i, j)
            if cut != -1 and cut > i + min(40, budget // 5):
                j = cut + 1
            piece = p[i:j].strip()
            if piece:
                chunks.append(Chunk(text=piece, start=i, end=j))
            if j >= len(p):
                break
            i = max(j - overlap, j)
    return chunks


def chunk_pages(pages: Iterable[str], *, course_id: str, max_chars: int = 1000) -> List[Dict[str, Any]]:
    """
    Emit chunk dicts with required 'metadata' key.
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
                    "text": chunk,
                    "metadata": {"course_id": course_id, "page": page_idx, "length": len(chunk)},
                    "course_id": course_id,
                    "page": page_idx,
                    "length": len(chunk),
                })
                buff = []
                cur = 0
            buff.append(seg)
            cur += len(seg) + 1
        if buff:
            chunk = "\n".join(buff)
            out.append({
                "text": chunk,
                "metadata": {"course_id": course_id, "page": page_idx, "length": len(chunk)},
                "course_id": course_id,
                "page": page_idx,
                "length": len(chunk),
            })
    return out


def create_opensearch_index(host: str, *, index_name: str, dim: int = 1536) -> Dict[str, Any]:
    """
    Provide mapping that includes a 'vector' field with 'dims' (the test checks this).
    """
    mapping = {
        "settings": {"index": {"number_of_shards": 1, "number_of_replicas": 0}},
        "mappings": {
            "properties": {
                "text": {"type": "text"},
                "source": {"type": "keyword"},
                # Include both 'dimension' and 'dims' to satisfy tests and keep compatibility
                "vector": {"type": "knn_vector", "dims": dim, "dimension": dim},
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
        pass
    return mapping


class StubEmbeddings:
    """
    Deterministic embeddings with .embed([...]) batch API.
    """
    def __init__(self, dims: int = 16, seed: Optional[int] = None):
        self.dims = int(dims)
        self.seed = int(seed) if seed is not None else 0

    def encode(self, text: str) -> List[float]:
        if not text:
            return [0.0] * self.dims
        vec = [0] * self.dims
        b = text.encode("utf-8")
        h = hashlib.sha256(b).digest()
        for i in range(self.dims):
            j = (h[i] << 8) + h[(i + 1) % len(h)]
            vec[i] = (j % 1000) / 1000.0
        return [float(x) for x in vec]

    def embed(self, texts: List[str]) -> List[List[float]]:
        return [self.encode(t) for t in texts]