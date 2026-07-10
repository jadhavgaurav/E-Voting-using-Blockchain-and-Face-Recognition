# syntax=docker/dockerfile:1
FROM python:3.12-slim

# Install uv (fast Python package manager).
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    PORT=8100

WORKDIR /app

# Install dependencies first for better layer caching.
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --no-install-project

# Copy the application source and install the project itself.
COPY app ./app
RUN uv sync --frozen --no-dev

EXPOSE 8100

# Run the service. Enable the real model with `uv sync --extra insightface`
# and FACE_EMBEDDER=insightface at build/run time.
CMD ["uv", "run", "--no-dev", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8100"]
