# Embeddings

This page describes embedding provider considerations and the scaffold's stub implementation.

Stub embedding

- backend/app/ingest.py defines StubEmbeddings with a deterministic sha256-based vector.
- Use this for unit tests and offline development.

Swapping to production providers

- Provide an adapter that implements embed(texts: List[str]) -> List[List[float]].
- Example providers: OpenAI embeddings, Bedrock embedding models.

Dimension and mapping

- Typical dim: 1536 for OpenAI/Bedrock. The scaffold uses a default of 1536 for index mapping but the StubEmbeddings defaults to a smaller dim for speed.
- Ensure index mapping matches vector dims when creating the OpenSearch index (create_opensearch_index).

Where to edit

!!! info "Where to edit"
- Stub & adapters: backend/app/ingest.py
- Index mapping: backend/app/ingest.py:create_opensearch_index
