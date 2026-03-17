# Stage 1: Build the React application
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app ./app
COPY ./init_db.py .

# Expose FastAPI port
EXPOSE 8000

# Run the DB init script, then start Gunicorn
CMD ["sh", "-c", "python init_db.py && gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --timeout 120"]

