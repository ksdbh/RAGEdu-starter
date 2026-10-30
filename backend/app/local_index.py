"""Persistent offline keyword retrieval. No embeddings, network, or model calls."""
from __future__ import annotations

import re
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any

STOP_WORDS = frozenset(
    "a an and are as at be by can do does explain for from how i in is it of on or "
    "the this to was what when where which who why with about please tell me".split()
)


def query_terms(text: str) -> list[str]:
    return list(dict.fromkeys(
        term for term in re.findall(r"[^\W_]+", text.lower(), flags=re.UNICODE)
        if term not in STOP_WORDS and len(term) > 1
    ))[:64]


def validate_course_id(course_id: str) -> str:
    course_id = course_id.strip()
    if not course_id or len(course_id) > 100 or not course_id.isprintable():
        raise ValueError("course_id must contain 1..100 printable characters")
    return course_id


class LocalIndex:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def _read(self) -> sqlite3.Connection:
        # Read-only queries never silently create a new database at a wrong path.
        connection = sqlite3.connect(self.path.resolve().as_uri() + "?mode=ro", uri=True)
        connection.row_factory = sqlite3.Row
        return connection

    def replace_document(self, *, course_id: str, document_id: str, source: str,
                         title: str, chunks: list[dict[str, Any]]) -> None:
        course_id = validate_course_id(course_id)
        if not chunks:
            raise ValueError("No extractable text found; OCR/scanned PDFs are not supported")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(self.path)) as connection, connection:
            connection.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS passages USING fts5(
                    text, course_id UNINDEXED, document_id UNINDEXED,
                    source UNINDEXED, title UNINDEXED, page UNINDEXED,
                    section UNINDEXED, chunk_id UNINDEXED,
                    tokenize='unicode61'
                )
            """)
            connection.execute(
                "DELETE FROM passages WHERE course_id = ? AND document_id = ?",
                (course_id, document_id),
            )
            connection.executemany(
                "INSERT INTO passages VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                [(chunk["text"], course_id, document_id, source, title,
                  chunk["metadata"]["page"], chunk["metadata"]["section"],
                  f"{document_id}:{i}") for i, chunk in enumerate(chunks)],
            )

    def courses(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        with closing(self._read()) as connection:
            return [dict(row) for row in connection.execute(
                "SELECT course_id, COUNT(DISTINCT document_id) AS documents, "
                "COUNT(*) AS passages FROM passages GROUP BY course_id ORDER BY course_id"
            )]

    def search(self, question: str, *, course_id: str, top_k: int = 5) -> list[dict[str, Any]]:
        course_id = validate_course_id(course_id)
        terms = query_terms(question)
        if not terms or not self.path.exists():
            return []
        expression = " OR ".join('"' + term + '"' for term in terms)
        with closing(self._read()) as connection:
            rows = connection.execute(
                "SELECT *, bm25(passages) AS rank FROM passages "
                "WHERE passages MATCH ? AND course_id = ? ORDER BY rank, chunk_id LIMIT ?",
                (expression, course_id, max(1, min(top_k, 20))),
            ).fetchall()
        return [{
            "title": row["title"], "page": int(row["page"]), "snippet": row["text"],
            "source": row["source"], "document_id": row["document_id"],
            "chunk_id": row["chunk_id"], "course_id": row["course_id"], "section": row["section"],
            "score": len(set(terms) & set(query_terms(row["text"]))) / len(terms),
        } for row in rows]
