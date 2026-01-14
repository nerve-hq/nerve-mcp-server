# Simple single-stage build like server/
FROM python:3.11-slim-bookworm

# Create non-root user
RUN groupadd -g 1001 appgroup && \
    useradd -u 1001 -g appgroup -m appuser

WORKDIR /app

# Install uv for fast dependency management
RUN pip install uv

# Copy everything
COPY pyproject.toml .
COPY uv.lock* .
COPY src/ ./src/
COPY .env.prod ./.env.prod

# Install dependencies (before switching user)
RUN uv pip install --system --no-cache .

# Change ownership
RUN chown -R appuser:appgroup /app

USER appuser

# Environment variables
ENV NERVE_MCP_ENV=prod
ENV NERVE_MCP_HOST=0.0.0.0
ENV NERVE_MCP_PORT=8000
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["python", "-m", "nerve_mcp"]
