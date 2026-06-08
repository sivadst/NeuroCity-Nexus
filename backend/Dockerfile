# Use the official Python 3.11 slim image as the backend runtime base.
FROM python:3.11-slim

# Keep Python predictable inside containers.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install build dependencies required by psycopg and common Python packages.
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# All backend source code lives under /app.
WORKDIR /app

# Install Python dependencies before copying source to improve layer caching.
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the backend application into the image.
COPY . .

# Expose the FastAPI development port.
EXPOSE 8000

# Run the API with live reload for local development.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
