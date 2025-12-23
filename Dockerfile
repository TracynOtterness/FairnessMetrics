FROM python:3.11-slim

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency files first for layer caching
COPY pyproject.toml uv.lock README.md ./

# Install dependencies (frozen from lock file)
RUN uv sync --frozen --no-dev

# Copy application code
COPY . .

EXPOSE 5000

CMD ["uv", "run", "python", "run.py"]
