# Stage 1: Build the React application
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app ./app
COPY ./init_db.py .
COPY ./migrate_v2.py .
COPY ./migrate_v2_1.py .

# JMc - 2026-03-18 - Cloud Run dynamically assigns a PORT environment variable (default 8080).
# We must bind Gunicorn to this dynamic variable, not a hardcoded port.
# Also removed `python init_db.py` from boot sequence to prevent 5-minute timeouts on massive historical syncs.
# Bumped timeout to 300s to handle deep-history Markov scoring on large datasets.
# JMc - 2026-03-31 - Reduced workers to 2 to prevent DB connection exhaustion on small instances.
CMD ["sh", "-c", "gunicorn app.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-8000} --timeout 300"]

