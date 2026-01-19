# Guide: Switch vector store

This guide will eventually cover migrating from the default OpenSearch-based
vector store to another service (or a managed OpenSearch deployment), including:

- Understanding how the current OpenSearch index is created.
- Adapting the retrieval and indexing code to a new provider.
- Re-running ingestion safely for existing courses.

For the moment, refer to `backend/app/ingest.py` and `backend/app/rag.py` for
how vector indices and retrieval are wired today.
