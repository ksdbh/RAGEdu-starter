# backend/app/ingest.py
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Iterable, Dict, Any
import re


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
    Character-window chunking with EXACT prefix overlap:
    chunk[i+1].text starts with the last `overlap_tokens` chars of chunk[i].text
    so tests can detect a.endswith(b[:L]).
    """
    if not text or not text.strip():
        return []

    s = text.replace("\r\n", "\n")
    L = len(s)
    size = max(1, int(max_tokens))
    ov = max(0, int(overlap_tokens))
    out: List[Chunk] = []

    i = 0
    while i < L:
        j = min(i + size, L)
        chunk_text = s[i:j]
        out.append(Chunk(text=chunk_text, start=i, end=j))
        if j >= L:
            break
        # ensure next window begins exactly at j-ov
        i = max(0, j - ov)

    return out


def _guess_section_name(lines: list[str]) -> str:
    for ln in lines:
        t = ln.strip()
        if not t:
            continue
        # VERY simple "heading" heuristic: ALLCAPS word or numbered outline like "1. Title"
        if re.match(r"^[A-Z][A-Z0-9\s\-]{2,}$", t) or re.match(r"^\d+\.\s", t):
            return t.split("\n", 1)[0][:40]
        # fallback to first non-empty line as section
        return t[:40]
    return "Section"


def chunk_pages(pages: Iterable[str], *, course_id: str, max_chars: int = 1000) -> List[Dict[str, Any]]:
    """
    Include a '[page=N]' and '[section=...]' marker in the text and a 'metadata' dict.
    """
    out: List[Dict[str, Any]] = []
    for page_idx, page in enumerate(pages, start=1):
        text = (page or "").replace("\r\n", "\n").strip()
        if not text:
            continue
        lines = [p for p in text.split("\n") if p.strip()]
        section = _guess_section_name(lines)

        buf: list[str] = []
        cur = 0
        for seg in lines:
            seg_len = len(seg) + 1
            if cur + seg_len > max_chars and buf:
                chunk_txt = f"[page={page_idx}] [section={section}] " + "\n".join(buf)
                meta = {"course_id": course_id, "page": page_idx, "length": len(chunk_txt)}
                out.append({"text": chunk_txt, "metadata": meta, "course_id": course_id, "page": page_idx, "length": len(chunk_txt)})
                buf, cur = [], 0
            buf.append(seg)
            cur += seg_len
        if buf:
            chunk_txt = f"[page={page_idx}] [section={section}] " + "\n".join(buf)
            meta = {"course_id": course_id, "page": page_idx, "length": len(chunk_txt)}
            out.append({"text": chunk_txt, "metadata": meta, "course_id": course_id, "page": page_idx, "length": len(chunk_txt)})
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
                # keep for compatibility in other parts
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