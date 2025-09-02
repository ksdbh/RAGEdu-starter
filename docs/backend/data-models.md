# Data models

This file points to the primary Python modules that define runtime data models.

Primary sources

- backend/app/db.py — CourseSyllabusStore and data storage helpers
- backend/app/ingest.py — Chunk dataclass and chunking helpers
- backend/app/auth.py — User model (pydantic) and auth interfaces

Common model shapes

- Chunk (in memory representation)
  - text: string
  - start: int
  - end: int

- Course / Syllabus
  - course_id: string
  - title: string
  - metadata: object

Where to edit

!!! info "Where to edit"
- Source models: backend/app/**/*.py
- DB: backend/app/db.py
- Ingest: backend/app/ingest.py

<!-- TODO: If you introduce pydantic models for API payloads, place them in backend/app/models.py. Owner: @backend-owner -->
