# Test conventions

Conventions to follow when adding tests.

Naming

- Test files: tests/test_*.py
- Test functions: test_<behavior>

Fixtures

- Use pytest fixtures for shared setup (client, mock embeddings, mock auth).

Mocks & stubs

- Use MockCognitoClient for auth; set environment USE_IN_MEMORY_DB=1 for db tests.

Where to edit

!!! info "Where to edit"
- Conventions: docs/testing/test-conventions.md
- Example fixtures: backend/tests/conftest.py (create if missing)
