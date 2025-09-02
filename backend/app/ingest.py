# backend/app/ingest.py
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Iterable, Dict, Any


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
    Produce character-based overlapping windows with a `.text` attribute
    so tests can verify overlap between adjacent chunks.
    """
    if not text or not text.strip():
        return []

    s = text.replace("\r\n", "\n")
    L = len(s)
    size = max(1, int(max_tokens))
    ov = max(0, int(overlap_tokens))
    i = 0
    out: List[Chunk] = []
    while i < L:
        j = min(i + size, L)
        out.append(Chunk(text=s[i:j], start=i, end=j))
        if j >= L:
            break
        i = max(j - ov, j - 1)
    return out


def chunk_pages(pages: Iterable[str], *, course_id: str, max_chars: int = 1000) -> List[Dict[str, Any]]:
    """
    Include a '[page=N]' marker in the text and a 'metadata' dict.
    """
    out: List[Dict[str, Any]] = []
    for page_idx, page in enumerate(pages, start=1):
        text = (page or "").replace("\r\n", "\n").strip()
        if not text:
            continue
        parts = [p for p in text.split("\n") if p.strip()]
        buf: List[str] = []
        cur = 0
        for seg in parts:
            if cur + len(seg) + 1 > max_chars and buf:
                chunk_txt = "[page=%d] " % page_idx + "\n".join(buf)
                out.append({
                    "text": chunk_txt,
                    "metadata": {"course_id": course_id, "page": page_idx, "length": len(chunk_txt)},
                    "course_id": course_id,
                    "page": page_idx,
                    "length": len(chunk_txt),
                })
                buf = []
                cur = 0
            buf.append(seg)
            cur += len(seg) + 1
        if buf:
            chunk_txt = "[page=%d] " % page_idx + "\n".join(buf)
            out.append({
                "text": chunk_txt,
                "metadata": {"course_id": course_id, "page": page_idx, "length": len(chunk_txt)},
                "course_id": course_id,
                "page": page_idx,
                "length": len(chunk_txt),
            })
    return out


def create_opensearch_index(host: str, *, index_name: str, dim: int = 1536) -> Dict[str, Any]:
    """
    Mapping must include:
      - vector.dims == dim
      - course_id (keyword)
      - page (integer)
    """
    mapping = {
        "settings": {"index": {"number_of_shards": 1, "number_of_replicas": 0}},
        "mappings": {
            "properties": {
                "text": {"type": "text"},
                "source": {"type": "keyword"},
                "course_id": {"type": "keyword"},
                "page": {"type": "integer"},
                "vector": {"type": "knn_vector", "dims": dim},
                # keep a second field for broader compatibility
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
    Deterministic embeddings with a batch .embed([...]) method as required by tests.
    """
    def __init__(self, dims: int = 16):
        self.dims = int(dims)

    def _encode_one(self, text: str) -> List[float]:
        if not text:
            return [0.0] * self.dims
        import hashlib
        h = hashlib.sha256(text.encode("utf-8")).digest()
        vec = []
        for i in range(self.dims):
            j = (h[i] << 8) + h[(i + 1) % len(h)]
            vec.append((j % 1000) / 1000.0)
        return vec

    def embed(self, texts: List[str]) -> List[List[float]]:
        return [self._encode_one(t) for t in texts]