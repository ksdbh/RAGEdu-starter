import argparse
import hashlib
import json
import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

# Lightweight logging setup for CLI usage
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
logger = logging.getLogger("ingest")


@dataclass
class Chunk:
    id: str
    text: str
    start: int
    end: int
    metadata: Dict[str, Any]


# -------------------------
# PDF / Textract parser
# -------------------------

def parse_pdf_bytes(pdf_bytes: bytes, use_textract: bool = False) -> str:
    """Parse text out of PDF bytes.

    This is a best-effort parser. If use_textract is True and AWS credentials
    + Textract are available, this implementation would call Textract. For the
    scaffold we keep this as a safe stub that attempts a local fallback.

    The fallback attempts to import pypdf (PyPDF2 successor) if available and
    use it. If not available, we return a best-effort empty string (so CLI
    remains safe to run in environments without extra packages).
    """
    # Note: We intentionally avoid making a blocking dependency on AWS or third-party
    # PDF libs in this scaffold. If you want production parsing, implement
    # Textract StartDocumentTextDetection + job polling for PDFs or add pypdf to
    # requirements and use PdfReader.

    if use_textract:
        try:
            import boto3

            logger.info("Would call Textract to parse PDF (stub). Skipping actual call in scaffold.")
            # Real implementation: call StartDocumentTextDetection and poll for job completion.
            # We return a placeholder so the rest of the pipeline can run during local tests.
            return ""
        except Exception:
            logger.exception("Textract requested but failed; falling back to local parser.")

    # Local fallback using PyPDF (if installed).
    try:
        # PyPDF2 / pypdf packages expose PdfReader in different names; try common ones.
        try:
            from pypdf import PdfReader  # type: ignore
        except Exception:
            from PyPDF2 import PdfReader  # type: ignore

        reader = PdfReader(pdf_bytes if isinstance(pdf_bytes, str) else None)
        # If PdfReader accepts a stream of bytes, we'd pass io.BytesIO(pdf_bytes).
        # But to keep the scaffold tolerant, try both patterns.
    except Exception:
        try:
            from io import BytesIO
            from pypdf import PdfReader  # type: ignore

            reader = PdfReader(BytesIO(pdf_bytes))
        except Exception:
            try:
                from io import BytesIO
                from PyPDF2 import PdfReader  # type: ignore

                reader = PdfReader(BytesIO(pdf_bytes))
            except Exception:
                logger.info("No PDF parser available (pypdf / PyPDF2). Returning empty text.")
                return ""

    texts: List[str] = []
    try:
        for page in reader.pages:
            try:
                texts.append(page.extract_text() or "")
            except Exception:
                # Some readers have different APIs; be defensive
                texts.append("")
    except Exception:
        # Fallback if reader.pages not iterable; attempt to coerce
        logger.exception("Unexpected PDF reader shape; returning empty text.")
        return ""

    return "\n\f\n".join(texts)


# -------------------------
# Simple layout-aware semantic chunker
# -------------------------

def _estimate_tokens_for_text(text: str) -> int:
    # Very rough heuristic: 1 token ~ 4 characters (depends on tokenizer)
    return max(1, int(len(text) / 4))


def semantic_chunk_text(
    text: str,
    max_tokens: int = 500,
    overlap_tokens: int = 50,
) -> List[Chunk]:
    """Split text into semantic chunks.

    Behavior/heuristics:
    - Prefer splitting on paragraph boundaries (double newline) and explicit page
      separators (form feed '\f').
    - Break paragraphs into sentence-like units if a paragraph is too large.
    - Ensure approximate token budget per chunk (using a simple char->token heuristic).
    - Add overlap in tokens between consecutive chunks.

    Returns a list of Chunk dataclasses, each with start/end character offsets.
    """
    if not text:
        return []

    # Normalize different page markers to a paragraph delimiter
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Split into paragraphs by double-newline or form feed (common PDF page boundary)
    paragraphs: List[str] = []
    for part in text.split("\f"):
        for p in part.split("\n\n"):
            p = p.strip()
            if p:
                paragraphs.append(p)

    # If no double-newline style paragraphs, split by single newlines but keep lines that are short
    if not paragraphs and "\n" in text:
        paragraphs = [ln.strip() for ln in text.split("\n") if ln.strip()]

    max_chars = max(32, max_tokens * 4)  # guard lower bound
    overlap_chars = max(0, overlap_tokens * 4)

    chunks: List[Chunk] = []
    cursor = 0  # global character offset in the normalized text

    # We'll reconstruct the normalized text to calculate offsets reliably
    normalized_text = "\n\n".join(paragraphs)

    pos = 0
    for para in paragraphs:
        para_start = normalized_text.find(para, pos)
        if para_start == -1:
            # fallback to current pos
            para_start = pos
        para_end = para_start + len(para)
        pos = para_end

        if len(para) <= max_chars:
            chunks.append(Chunk(id="", text=para, start=para_start, end=para_end, metadata={}))
            continue

        # Paragraph is too long; split into sentence-like pieces
        import re

        sentence_boundaries = re.split(r"(?<=[.!?])\s+", para)
        current_piece = ""
        piece_start_in_para = 0
        running_idx = 0
        for sent in sentence_boundaries:
            if not sent:
                continue
            if len(current_piece) + len(sent) + 1 <= max_chars:
                if not current_piece:
                    piece_start_in_para = running_idx
                    current_piece = sent
                else:
                    current_piece = current_piece + " " + sent
            else:
                # flush current_piece
                start = para_start + piece_start_in_para
                end = start + len(current_piece)
                chunks.append(Chunk(id="", text=current_piece, start=start, end=end, metadata={}))
                # start new piece
                piece_start_in_para = running_idx
                current_piece = sent
            running_idx += len(sent) + 1  # account for the separator

        if current_piece:
            start = para_start + piece_start_in_para
            end = start + len(current_piece)
            chunks.append(Chunk(id="", text=current_piece, start=start, end=end, metadata={}))

    # Now merge small adjacent chunks to better utilize space and add overlap
    merged: List[Chunk] = []
    for c in chunks:
        if not merged:
            merged.append(c)
            continue
        last = merged[-1]
        # If combined size still within max_chars, merge them
        if len(last.text) + 1 + len(c.text) <= max_chars:
            new_text = last.text + " " + c.text
            new_chunk = Chunk(id="", text=new_text, start=last.start, end=c.end, metadata={})
            merged[-1] = new_chunk
        else:
            merged.append(c)

    # Add deterministic ids and adjust for overlap
    final_chunks: List[Chunk] = []
    for i, c in enumerate(merged):
        # compute id as hash of text + course if present (metadata may supply course later)
        h = hashlib.sha256(c.text.encode("utf-8")).hexdigest()[:12]
        chunk_id = f"chunk_{i}_{h}"
        c.id = chunk_id
        final_chunks.append(c)

    # Create overlapping copies: we'll represent overlap by including overlap text in the next chunk's text
    if overlap_chars > 0 and len(final_chunks) > 1:
        overlapped: List[Chunk] = []
        for i, c in enumerate(final_chunks):
            text = c.text
            start = c.start
            end = c.end
            if i > 0:
                # prepend overlap from previous chunk
                prev = overlapped[-1]
                # compute overlap slice from prev.text (last overlap_chars)
                overlap_text = prev.text[-overlap_chars:] if overlap_chars < len(prev.text) else prev.text
                if overlap_text and not text.startswith(overlap_text):
                    text = overlap_text + " " + text
                    # adjust start backward for accurate offsets (approximate)
                    start = max(0, start - len(overlap_text) - 1)
            overlapped.append(Chunk(id=c.id, text=text, start=start, end=end, metadata=c.metadata))
        final_chunks = overlapped

    return final_chunks


# -------------------------
# Embeddings (Bedrock Titan stub)
# -------------------------

class BedrockEmbeddingClientStub:
    """Stub for Bedrock Titan embeddings.

    In the real implementation you'd call Bedrock to get embeddings for each
    chunk. For the scaffold we provide deterministic pseudo-embeddings derived
    from stable hashes so unit tests and local runs are repeatable.
    """

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        embeddings: List[List[float]] = []
        for t in texts:
            # deterministic pseudo-embedding: take sha256 and convert bytes to floats in [-1,1]
            digest = hashlib.sha256(t.encode("utf-8")).digest()
            vec = [((b / 255.0) * 2.0 - 1.0) for b in digest[:32]]  # 32-d vector
            embeddings.append(vec)
        return embeddings


# -------------------------
# OpenSearch indexer (stub / lightweight)
# -------------------------

class OpenSearchIndexerStub:
    """Stub indexer. In production use opensearch-py to index vectors + metadata.

    This stub records the documents it would index so tests or local inspection can
    validate behavior without a running OpenSearch cluster.
    """

    def __init__(self):
        self.indexed: List[Dict[str, Any]] = []

    def index_chunks(self, index_name: str, chunks: List[Chunk], embeddings: List[List[float]], course_id: Optional[str] = None):
        assert len(chunks) == len(embeddings), "chunks and embeddings length mismatch"
        for c, emb in zip(chunks, embeddings):
            doc = {
                "chunk_id": c.id,
                "text": c.text,
                "start": c.start,
                "end": c.end,
                "embedding": emb,
                "course_id": course_id,
            }
            self.indexed.append(doc)
        logger.info("Indexed %d chunks into %s (stub).", len(chunks), index_name)
        return True


# -------------------------
# Top-level ingestion orchestration
# -------------------------

def ingest_file(path: str, course_id: Optional[str] = None, use_textract: bool = False) -> Dict[str, Any]:
    """Run the ingestion pipeline for a single file.

    Steps (scaffold):
    1. Read bytes from provided path.
    2. Parse text (Textract stub or local fallback).
    3. Chunk text semantically.
    4. Create embeddings via Bedrock stub.
    5. Index to OpenSearch stub.

    Returns a dictionary with summary info for CLI-friendly output.
    """
    logger.info("Starting ingestion for %s (course=%s)", path, course_id)

    if not os.path.exists(path):
        raise FileNotFoundError(path)

    with open(path, "rb") as fh:
        pdf_bytes = fh.read()

    text = parse_pdf_bytes(pdf_bytes, use_textract=use_textract)
    if not text:
        logger.warning("No text extracted from PDF; continuing with empty text.")

    chunks = semantic_chunk_text(text, max_tokens=500, overlap_tokens=50)
    logger.info("Produced %d chunks", len(chunks))

    bedrock = BedrockEmbeddingClientStub()
    embeddings = bedrock.embed_texts([c.text for c in chunks])

    indexer = OpenSearchIndexerStub()
    index_name = f"ragedu-docs-{course_id or 'global'}"
    indexer.index_chunks(index_name, chunks, embeddings, course_id=course_id)

    summary = {
        "path": path,
        "course_id": course_id,
        "num_chunks": len(chunks),
        "indexed_docs": len(indexer.indexed),
        "index_name": index_name,
    }

    logger.info("Ingestion summary: %s", json.dumps(summary))
    return summary


# -------------------------
# CLI entrypoint
# -------------------------

def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m app.ingest", description="Ingest a PDF into the RAGEdu vector index (scaffold)")
    parser.add_argument("path", help="Path to the PDF file to ingest")
    parser.add_argument("--course", dest="course", default=None, help="Optional course id to associate with this document")
    parser.add_argument("--use-textract", dest="use_textract", action="store_true", help="(Stub) Use Textract for parsing when available")

    args = parser.parse_args(argv)

    try:
        summary = ingest_file(args.path, course_id=args.course, use_textract=args.use_textract)
        print(json.dumps(summary, indent=2))
        return 0
    except Exception as e:
        logger.exception("Ingestion failed: %s", e)
        print({"error": str(e)})
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
