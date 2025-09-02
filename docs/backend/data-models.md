# Data models

This page links to and summarizes key data models used by the backend. For full edits, update the source models under backend/app/**/*.py.

Key in-repo models

- User (Pydantic): backend/app/auth.py — User model with sub, username, email, role, roles.
- Chunk / ingestion objects: backend/app/ingest.py — Chunk dataclass, chunk_pages output format.
- DB store: backend/app/db.py — CourseSyllabusStore: create_course, get_course, create_syllabus, get_syllabus (in-memory by default).

Where to edit

!!! info "Where to edit"
    Source: docs/backend/data-models.md
    Files: backend/app/auth.py, backend/app/ingest.py, backend/app/db.py
