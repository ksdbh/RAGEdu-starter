FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install deps
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY backend/ ./backend/

# Make both 'app' and 'backend.app' importable
# - '/app/backend' lets "import app" find backend/app/
# - '/app' still allows "import backend.app" if used elsewhere
ENV PYTHONPATH=/app/backend:/app

EXPOSE 8000

# Run using the 'app' import path so both styles work
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]