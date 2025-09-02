/gen Replace backend/Dockerfile with:

FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install deps
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code into /app/backend so "backend" is a top-level package
COPY backend/ ./backend/

# Ensure Python can import the "backend" package
ENV PYTHONPATH=/app

EXPOSE 8000

# CI-friendly: no reload, deterministic port
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]