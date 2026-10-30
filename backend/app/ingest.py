# backend/app/ingest.py
from __future__ import annotations

from dataclasses import dataclass
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
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
    if not text or not text.strip():
        return []

    s = text.replace("\r\n", "\n")
    L = len(s)
    size = max(1, int(max_tokens))
    ov = max(0, int(overlap_tokens))
    if ov >= size:
        raise ValueError("overlap_tokens must be smaller than max_tokens")
    out: List[Chunk] = []

    i = 0
    while i < L:
        j = min(i + size, L)
        chunk_text = s[i:j]
        out.append(Chunk(text=chunk_text, start=i, end=j))
        if j >= L:
            break
        i = max(0, j - ov)

    return out


def _guess_section_name(lines: list[str]) -> str:
    for ln in lines:
        t = ln.strip()
        if not t:
            continue
        if re.match(r"^[A-Z][A-Z0-9\s\-]{2,}$", t) or re.match(r"^\d+\.\s", t):
            return t.split("\n", 1)[0][:40]
        return t[:40]
    return "Section"


def chunk_pages(pages: Iterable[str], *, course_id: str, max_chars: int = 1000) -> List[Dict[str, Any]]:
    if max_chars < 1:
        raise ValueError("max_chars must be positive")
    out: List[Dict[str, Any]] = []
    for page_idx, page in enumerate(pages, start=1):
        text = (page or "").replace("\r\n", "\n").strip()
        if not text:
            continue
        section = _guess_section_name(text.splitlines())
        # The text budget is measured in characters, not semantic tokens.
        for start in range(0, len(text), max_chars):
            chunk_txt = text[start:start + max_chars]
            meta = {"course_id": course_id, "page": page_idx, "length": len(chunk_txt), "section": section}
            out.append({"text": chunk_txt, "metadata": meta, **{k: meta[k] for k in ("course_id", "page", "length")}})
    return out


def create_opensearch_index(host: str, *, index_name: str, dim: int = 1536) -> Dict[str, Any]:
    mapping = {
        "settings": {"index": {"number_of_shards": 1, "number_of_replicas": 0}},
        "mappings": {
            "properties": {
                "text": {"type": "text"},
                "source": {"type": "keyword"},
                "course_id": {"type": "keyword"},
                "page": {"type": "integer"},
                "vector": {"type": "knn_vector", "dims": dim},
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


def ingest_pdf(path: str | Path, *, course_id: str, index_path: str | Path,
               title: str | None = None, max_chars: int = 1000) -> Dict[str, Any]:
    """Parse a text PDF and atomically replace its passages in a local index.

    Document identity is content-based; reimporting identical bytes into the
    same course is idempotent. Changed bytes create a distinct document.
    """
    from pypdf import PdfReader
    from .local_index import LocalIndex, validate_course_id

    course_id = validate_course_id(course_id)
    source = Path(path)
    if source.suffix.lower() != ".pdf":
        raise ValueError("Only PDF files are supported")
    payload = source.read_bytes()
    if len(payload) > 25 * 1024 * 1024:
        raise ValueError("PDF exceeds the 25 MiB local ingestion limit")
    import io
    reader = PdfReader(io.BytesIO(payload))
    if reader.is_encrypted:
        raise ValueError("Encrypted PDFs are not supported")
    pages = [page.extract_text() or "" for page in reader.pages]
    chunks = chunk_pages(pages, course_id=course_id, max_chars=max_chars)
    document_id = hashlib.sha256(payload).hexdigest()
    LocalIndex(index_path).replace_document(
        course_id=course_id, document_id=document_id, source=source.name,
        title=(title or source.stem).strip() or source.stem, chunks=chunks,
    )
    return {"course_id": course_id, "document_id": document_id,
            "source": source.name, "pages": len(pages), "passages": len(chunks)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Index a text PDF locally; no AWS or model calls")
    parser.add_argument("file", type=Path)
    parser.add_argument("--course", required=True)
    parser.add_argument("--title")
    parser.add_argument("--index", default=os.environ.get("RAGEDU_INDEX_PATH", "data/courses.sqlite3"))
    parser.add_argument("--max-chars", type=int, default=1000)
    args = parser.parse_args(argv)
    try:
        result = ingest_pdf(args.file, course_id=args.course, index_path=args.index,
                            title=args.title, max_chars=args.max_chars)
    except Exception as exc:
        print(f"Ingestion failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
