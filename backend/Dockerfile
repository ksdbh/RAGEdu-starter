# syntax=docker/dockerfile:1

# ---- Builder: install python deps into a relocatable prefix ----
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install minimal build deps (kept small for slim image)
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp

# Copy only requirements first so layer caches when deps don't change
COPY requirements.txt ./

# Upgrade pip and install into a separate prefix so we can copy just site-packages to final image
RUN pip install --upgrade pip \
    && pip install --prefix=/install -r requirements.txt


# ---- Final: copy installed packages + app, run as non-root ----
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create a dedicated non-root user
RUN addgroup --system app \
    && adduser --system --ingroup app app

# Bring installed packages from builder
COPY --from=builder /install /usr/local

WORKDIR /app

# Copy application code (chown so non-root user can read/write where appropriate)
COPY --chown=app:app . .

# Switch to non-root user
USER app

# Default port for FastAPI / uvicorn
EXPOSE 8000

# Default command to run the FastAPI app. The repo's development workflows expect port 8000.
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
