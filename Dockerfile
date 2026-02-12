# ----------------------
# Stage 1: Base
# ----------------------
FROM python:3.11-slim AS base

# Set working directory
WORKDIR /app

# Copy only requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source code, tests, and alembic for migrations
COPY app ./app
COPY tests ./tests
COPY alembic ./alembic

# ----------------------
# Stage 2: Test
# ----------------------
FROM base AS test

# Install testing dependencies
RUN pip install --no-cache-dir pytest pytest-asyncio httpx

# Default command for running tests
CMD ["pytest", "-v"]

# ----------------------

# ----------------------
FROM base AS prod

# Expose FastAPI port
EXPOSE 8000

# Command to run FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
