# Testing overview

Testing strategy

- Unit tests: fast, no AWS calls. Use stubs (MockCognitoClient, StubEmbeddings).
- Integration tests: optional, can exercise docker-compose CI or LocalStack.
- End-to-end: deploy to test/staging with real AWS resources and run smoke tests.

Where tests live

- backend/tests/ — pytest tests for backend
- frontend/ — frontend tests (if present)

Where to edit

!!! info "Where to edit"
- Test docs: docs/testing/overview.md
- Test files: backend/tests/
