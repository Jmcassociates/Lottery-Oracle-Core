# Stage 1: Build the React application
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app ./app
COPY ./init_db.py .

# JMc - 2026-03-18 - Cloud Run dynamically assigns a PORT environment variable (default 8080).
# We must bind Gunicorn to this dynamic variable, not a hardcoded port.
CMD ["sh", "-c", "python init_db.py && gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-8000} --timeout 120"]

