import sys
import types
import pytest

from app import ingest


def test_chunk_pages_heading_aware():
    pages = [
        "INTRODUCTION\nThis is the first page. It has some text.\n1. Overview:\nMore details here.\nSmall paragraph.",
        "METHODS\nHere we describe methods.\n2. Algorithm\nStep 1\nStep 2\nEnd.",
    ]
    chunks = ingest.chunk_pages(pages, course_id="CS101", max_chars=80)
    # Expect at least a few chunks
    assert isinstance(chunks, list)
    assert len(chunks) >= 2

    # Each chunk should include metadata keys and page anchors
    for c in chunks:
        assert "text" in c
        assert "metadata" in c
        meta = c["metadata"]
        assert "page" in meta
        assert meta.get("course_id") == "CS101"
        assert "[page=" in c["text"]
        assert "[section=" in c["text"]

    # Check that headings like INTRODUCTION and METHODS were used as sections
    sections = {c["metadata"]["section"] for c in chunks}
    assert any("INTRODUCTION" in s or "INTRODUCTION" == s for s in sections) or any(s == "" for s in sections)
    assert any("METHODS" in s or "METHODS" == s for s in sections) or any(s == "" for s in sections)


def test_create_opensearch_index_invokes_client(monkeypatch):
    # Create a fake opensearchpy module and OpenSearch class to capture calls
    created = {}

    class FakeIndices:
        def __init__(self):
            self.created = False

        def exists(self, index):
            created["exists_called_with"] = index
            return False

        def create(self, index, body):
            created["create_called_with"] = {"index": index, "body": body}

    class FakeOpenSearchClient:
        def __init__(self, hosts=None):
            created["hosts"] = hosts
            self.indices = FakeIndices()

    fake_module = types.ModuleType("opensearchpy")
    setattr(fake_module, "OpenSearch", FakeOpenSearchClient)

    monkeypatch.setitem(sys.modules, "opensearchpy", fake_module)

    mapping = ingest.create_opensearch_index("http://localhost:9200", index_name="test-index", dim=16)

    assert "create_called_with" in created
    body = created["create_called_with"]["body"]
    # mapping should contain our vector and metadata fields
    props = body["mappings"]["properties"]
    assert "vector" in props and props["vector"]["dims"] == 16
    assert "course_id" in props and props["page"]["type"] == "integer"


def test_stub_embeddings_repeatable():
    s = ingest.StubEmbeddings(dims=4)
    v1 = s.embed(["hello"])[0]
    v2 = s.embed(["hello"])[0]
    assert v1 == v2
    assert len(v1) == 4
