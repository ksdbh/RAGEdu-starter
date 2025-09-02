# Getting Started — Local development

This page provides a short, prescriptive path to run EduRAG locally.

Prerequisites

- Git
- Python 3.11
- Node 20 + npm
- Docker (optional for devcontainer or LocalStack)

1) Clone the repo

```bash
git clone https://github.com/your-org/your-repo.git
cd your-repo
```

2) Devcontainer (recommended)

Open the repo in VS Code and use the included devcontainer. The container will run:

```bash
pip install -r backend/requirements.txt && cd frontend && npm i
```

3) Backend (local)

```bash
# optional: create venv
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
# run with hot reload
uvicorn backend.app.main:app --reload --port 8000
```

4) Frontend (local)

```bash
cd frontend
npm ci
export NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
npm run dev
```

Local tokens (mock auth)

- student_token (role: student)
- prof_token (role: professor)
- admin_token (role: professor)
- custom: mock:alice|professor

Example curl (whoami)

```bash
curl -H "Authorization: Bearer student_token" http://localhost:8000/whoami
```

Where to edit

!!! info "Where to edit"
    Source: docs/getting-started.md
    Back-end startup: backend/app/main.py
    Ingest CLI: backend/app/ingest.py
