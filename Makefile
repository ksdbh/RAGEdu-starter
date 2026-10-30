.PHONY: help devcontainer-setup backend-install backend-run backend-test ingest frontend-install frontend-dev frontend-build infra-plan infra-apply infra-destroy lint format

help:
	@echo "Available targets:"
	@echo "  devcontainer-setup   - Run backend deps install & frontend npm install (same as devcontainer postCreateCommand)"
	@echo "  backend-install      - Create venv and install backend requirements"
	@echo "  backend-run          - Run FastAPI app (uvicorn) on localhost:8000"
	@echo "  backend-test         - Run backend pytest checks from the repository root"
	@echo "  ingest FILE=... COURSE=... - Index a local text PDF from the repository root"
	@echo "  frontend-install     - cd frontend && npm ci"
	@echo "  frontend-dev         - cd frontend && npm run dev"
	@echo "  frontend-build       - cd frontend && npm run build"
	@echo "  infra-plan/apply/destroy - Run terraform commands in infra/ if present"
	@echo "  lint                 - Run basic lint/format commands (if configured)"
	@echo "  format               - Run formatters (if configured)"

# Convenience: run same post-create steps as the devcontainer
devcontainer-setup:
	@echo "Running devcontainer setup: install backend reqs and frontend deps"
	@pip install -r backend/requirements.txt || true
	@cd frontend && npm i || true

# Backend
backend-install:
	@echo "Creating venv .venv (if missing) and installing backend requirements"
	@if [ ! -d ".venv" ]; then python -m venv .venv && . .venv/bin/activate && pip install -r backend/requirements.txt; else . .venv/bin/activate && pip install -r backend/requirements.txt; fi

backend-run:
	@echo "Starting FastAPI (uvicorn) on http://localhost:8000"
	@uvicorn backend.app.main:app --reload --port 8000

backend-test:
	@if [ -d backend ]; then python -m pytest -q; else echo "No backend directory found"; fi

# Index a local text PDF. Run from the repository root.
ingest:
	@if [ -z "$(FILE)" ] || [ -z "$(COURSE)" ]; then echo "Usage: make ingest FILE=path/to.pdf COURSE=CS101"; exit 1; fi
	@python -m backend.app.ingest "$(FILE)" --course "$(COURSE)"

# Frontend
frontend-install:
	@cd frontend && npm ci

frontend-dev:
	@cd frontend && npm run dev

frontend-build:
	@cd frontend && npm run build

# Terraform infra helpers (operate if infra/ exists)
infra-plan:
	@if [ -d infra ]; then cd infra && terraform init -input=false && terraform plan; else echo "No infra/ directory found"; fi

infra-apply:
	@if [ -d infra ]; then cd infra && terraform init -input=false && terraform apply -auto-approve; else echo "No infra/ directory found"; fi

infra-destroy:
	@if [ -d infra ]; then cd infra && terraform destroy -auto-approve; else echo "No infra/ directory found"; fi

# Lint / format (best-effort; tools may not be installed in the scaffold)
lint:
	@echo "Running lint (best-effort). Install tools if you want stricter checks."
	@if [ -d backend ]; then (command -v flake8 >/dev/null 2>&1 && flake8 backend) || echo "flake8 not available or passed"; fi
	@if [ -d frontend ]; then (cd frontend && command -v npm >/dev/null 2>&1 && npm run lint) || echo "frontend lint not configured or not available"; fi

format:
	@echo "Running formatters (best-effort). Install tools if desired."
	@if command -v black >/dev/null 2>&1 && [ -d backend ]; then black backend || true; else echo "black not available"; fi
	@if [ -d frontend ]; then (cd frontend && command -v npm >/dev/null 2>&1 && npm run format) || echo "frontend format not configured"; fi
