# Getting started (local dev)

This page walks you through getting the repository running locally. Follow these steps for a reproducible development environment.

Prerequisites

- Git
- Python 3.11
- Node 20 / npm
- Docker (optional; recommended for devcontainer)
- Make (optional but helpful)

Quick start (recommended)

1. Clone the repo

```bash
git clone https://github.com/your-org/your-repo.git
cd your-repo
```

2. Open the devcontainer (recommended)

- Use VS Code Remote - Containers and open the repository. The devcontainer will run the postCreateCommand which installs backend and frontend deps.

3. Local backend

```bash
# create venv (optional)
python -m venv .venv
source .venv/bin/activate

# install backend deps
pip install -r backend/requirements.txt

# run backend
uvicorn backend.app.main:app --reload --port 8000
```

4. Local frontend

```bash
cd frontend
npm ci
export NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
npm run dev
```

Authentication (local)

The scaffold uses MockCognitoClient for local dev. Use these bearer tokens in requests:

- student_token
- prof_token
- admin_token

Example curl

```bash
curl -H "Authorization: Bearer student_token" http://localhost:8000/whoami
```

Troubleshooting

- If an env var COGNITO_USER_POOL_ID is set, the app will attempt to use RealCognitoClient and may error if not configured.

Where to edit

!!! info "Where to edit"
- Dev instructions: docs/getting-started.md
- Backend run: backend/app/main.py
- Auth: backend/app/auth.py
