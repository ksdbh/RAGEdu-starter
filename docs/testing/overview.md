# Testing Overview

Strategy

- Unit tests: pure logic (chunking, embedding stubs, auth mockups)
- Integration tests: fast CI with stubs and docker compose (if available)
- E2E / smoke: run backend + frontend with sample data to exercise the RAG flow

Tools

- pytest for Python backend
- CI workflows run tests on PRs

Where to edit

!!! info "Where to edit"
    Source: docs/testing/overview.md
    Tests: backend/tests/
