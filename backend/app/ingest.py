import argparse
import hashlib
import logging
import os
import re
import sys
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("ingest")

# -----------------------------
# PDF parsing (pypdf fallback)
# -----------------------------

def parse_pdf(path: str, use_textract: bool = False) -> List[str]:
    """Return list of page texts (1-based pages: index 0 is page 1 text).

    - If use_textract is True, call a Textract stub (not implemented here).
    - Otherwise try pypdf PdfReader; on any import error or parsing error return []
    """
    if use_textract:
        logger.info("Textract mode requested; using textract_stub (best-effort)")
        return textract_stub(path)

    try:
        # local import to avoid forcing dependency at package import
        from pypdf import PdfReader  # type: ignore

        reader = PdfReader(path)
        pages = []
        for p in reader.pages:
            try:
                text = p.extract_text() or ""
            except Exception:
                # be tolerant of strange PDFs
                text = ""
            pages.append(text)
        logger.info("Parsed %d pages from %s", len(pages), path)
        return pages
    except Exception as e:
        logger.exception("Failed to parse PDF with pypdf: %s", e)
        return []


def textract_stub(path: str) -> List[str]:
    """Placeholder for Textract-based parsing.

    For the scaffold we provide a stub that currently behaves like an empty
    (no-op) extractor. Replace with a real Textract client/implementation when
    wiring AWS.
    """
    logger.info("textract_stub called for %s (not implemented)", path)
    return []


# -----------------------------
# Chunker: heading-aware
# -----------------------------


def _is_heading(line: str) -> bool:
    s = line.strip()
    if not s:
        return False
    # heuristic 1: short line that is mostly uppercase
    if len(s) < 120 and sum(c.isalpha() for c in s) >= 3 and s.upper() == s:
        return True
    # heuristic 2: numbered heading like '1.2 Foo' or '2) Bar'
    if re.match(r"^\d+[\d\.\)\-]*\s+.+", s):
        return True
    # heuristic 3: ends with ':' (labels)
    if s.endswith(":") and len(s) < 200:
        return True
    return False


def _slugify(s: str) -> str:
    s2 = s.strip().lower()
    s2 = re.sub(r"[^a-z0-9]+", "-", s2)
    s2 = re.sub(r"-+", "-", s2)
    return s2.strip("-")[:60]


def chunk_pages(
    pages: List[str], course_id: Optional[str] = None, max_chars: int = 1000
) -> List[Dict]:
    """Chunk a list of page texts into heading-aware passages.

    Returns list of dicts:
      {"text": ..., "metadata": {"course_id":..., "page": int, "section": str}}

    Each chunk will contain a page anchor at the top like: [page=1] [section=Intro]\n\n...
    """
    chunks: List[Dict] = []

    for page_idx, page_text in enumerate(pages, start=1):
        if not page_text:
            continue
        lines = page_text.splitlines()
        current_section = ""  # human-readable
        buffer_lines: List[str] = []

        def flush_section():
            nonlocal buffer_lines, current_section
            if not buffer_lines:
                return
            content = "\n".join(buffer_lines).strip()
            if not content:
                buffer_lines = []
                return
            section_key = current_section or ""  # keep empty if none
            anchor = f"page:{page_idx}#section:{_slugify(section_key) or 'none'}"
            text = f"[page={page_idx}] [section={section_key}] [anchor={anchor}]\n\n{content}"
            meta = {"page": page_idx, "section": section_key}
            if course_id:
                meta["course_id"] = course_id
            chunks.append({"text": text, "metadata": meta})
            buffer_lines = []

        for line in lines:
            if _is_heading(line):
                # treat heading as flush point (start a new section)
                # flush any buffered content as belonging to previous section
                flush_section()
                current_section = line.strip()
                continue

            # otherwise append line to buffer and flush if too large
            buffer_lines.append(line)
            if sum(len(l) for l in buffer_lines) > max_chars:
                flush_section()
        # end lines loop
        flush_section()

    return chunks


# -----------------------------
# Embeddings interface
# -----------------------------


class EmbeddingsInterface:
    def embed(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError()


class StubEmbeddings(EmbeddingsInterface):
    """Deterministic stub embeddings for CI/local tests.

    Produces low-dimensional vectors (default dim=8) derived from an md5
    hash of the text so results are repeatable across runs.
    """

    def __init__(self, dims: int = 8):
        self.dims = dims

    def embed(self, texts: List[str]) -> List[List[float]]:
        out: List[List[float]] = []
        for t in texts:
            h = hashlib.md5(t.encode("utf-8")).digest()
            vec: List[float] = []
            # expand bytes into dims floats in [-1,1]
            i = 0
            while len(vec) < self.dims:
                b = h[i % len(h)]
                val = (b / 255.0) * 2.0 - 1.0
                vec.append(round(val, 6))
                i += 1
            out.append(vec[: self.dims])
        return out


class BedrockEmbeddings(EmbeddingsInterface):
    """Skeleton for a Bedrock/Titan embeddings client.

    This is intentionally a placeholder. A full implementation would call
    Amazon Bedrock runtime/embeddings API and return float vectors.
    """

    def __init__(self, model: Optional[str] = None):
        # model could be configured via env var in real wiring
        self.model = model or os.environ.get("BACKEND_BEDROCK_MODEL")
        # Delay boto3 import until used to avoid hard dependency at import time
        try:
            import boto3  # type: ignore

            self._boto3 = boto3
        except Exception:
            self._boto3 = None
            logger.warning("boto3 not available; BedrockEmbeddings will not work")

    def embed(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError(
            "BedrockEmbeddings is a scaffold placeholder. Implement calling Bedrock runtime here."
        )


def get_embeddings_provider() -> EmbeddingsInterface:
    provider = os.environ.get("BACKEND_EMBEDDINGS_PROVIDER", "stub").lower()
    if provider == "bedrock":
        return BedrockEmbeddings()
    # default
    return StubEmbeddings()


# -----------------------------
# OpenSearch index bootstrap
# -----------------------------


def create_opensearch_index(host: str, index_name: str = "rage-docs", dim: int = 8) -> Dict:
    """Create an OpenSearch index with a vector field and our metadata.

    This function imports opensearchpy at runtime so the package is optional for
    environments that don't need it. It will raise ImportError if opensearchpy
    is not installed.
    """
    try:
        from opensearchpy import OpenSearch  # type: ignore
    except Exception as e:
        logger.exception("opensearchpy not available: %s", e)
        raise

    client = OpenSearch(hosts=[host])
    mapping = {
        "mappings": {
            "properties": {
                "vector": {"type": "dense_vector", "dims": dim},
                "course_id": {"type": "keyword"},
                "page": {"type": "integer"},
                "section": {"type": "keyword"},
            }
        }
    }

    if client.indices.exists(index=index_name):
        logger.info("Index %s already exists", index_name)
        return mapping

    logger.info("Creating OpenSearch index %s on %s", index_name, host)
    client.indices.create(index=index_name, body=mapping)
    return mapping


def index_documents_to_opensearch(host: str, index_name: str, docs: List[Dict], vectors: List[List[float]]):
    try:
        from opensearchpy import OpenSearch  # type: ignore
    except Exception as e:
        logger.exception("opensearchpy not available: %s", e)
        raise

    client = OpenSearch(hosts=[host])
    # build bulk payload
    bulk_lines: List[str] = []
    for doc, vec in zip(docs, vectors):
        meta = {"index": {"_index": index_name}}
        payload = {
            "text": doc["text"],
            "vector": vec,
            **doc["metadata"],
        }
        bulk_lines.append(_json_dumps(meta))
        bulk_lines.append(_json_dumps(payload))

    body = "\n".join(bulk_lines) + "\n"
    client.bulk(body=body)


def _json_dumps(o: object) -> str:
    # delayed import to minimize top-level deps
    import json

    return json.dumps(o)


# -----------------------------
# CLI
# -----------------------------


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser("ingest")
    parser.add_argument("file", help="PDF file to ingest")
    parser.add_argument("--course", help="optional course id to attach as metadata", default=None)
    parser.add_argument("--index", help="OpenSearch index name", default="rage-docs")
    parser.add_argument("--use-textract", action="store_true", help="Use Textract (stub) instead of pypdf")
    parser.add_argument("--max-chars", type=int, default=1000, help="Max chars per chunk")
    args = parser.parse_args(argv)

    pages = parse_pdf(args.file, use_textract=args.use_textract)
    if not pages:
        logger.warning("No pages parsed from %s; exiting", args.file)
        return 1

    chunks = chunk_pages(pages, course_id=args.course, max_chars=args.max_chars)
    if not chunks:
        logger.warning("No chunks generated from %s; exiting", args.file)
        return 1

    embed_provider = get_embeddings_provider()
    texts = [c["text"] for c in chunks]
    vectors = embed_provider.embed(texts)

    os_host = os.environ.get("BACKEND_OS_HOST")
    if not os_host:
        logger.info(
            "BACKEND_OS_HOST not configured; skipping OpenSearch indexing. Generated %d chunks.\nUse BACKEND_OS_HOST to enable indexing.",
            len(chunks),
        )
        # For local convenience write a small summary
        for i, c in enumerate(chunks[:5], start=1):
            logger.info("Chunk %d meta=%s text_preview=%s", i, c["metadata"], c["text"][:120].replace("\n", " "))
        return 0

    # bootstrap index and index docs
    create_opensearch_index(os_host, index_name=args.index, dim=len(vectors[0]) if vectors else 8)
    index_documents_to_opensearch(os_host, args.index, chunks, vectors)
    logger.info("Ingestion complete: indexed %d chunks to %s/%s", len(chunks), os_host, args.index)
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    raise SystemExit(main())
