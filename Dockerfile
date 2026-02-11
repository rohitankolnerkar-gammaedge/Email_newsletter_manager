# ----------------------
# Stage 1: Base
# ----------------------
FROM python:3.11-slim AS base

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# ----------------------
# Stage 2: Test
# ----------------------
FROM base AS test

# Install testing dependencies
RUN pip install --no-cache-dir pytest pytest-asyncio httpx

# Default command for test stage
CMD ["pytest", "-v"]

# ----------------------
# Stage 3: Production
# ----------------------
FROM base AS prod

EXPOSE 8000

# Command to run FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
