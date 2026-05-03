# syntax=docker/dockerfile:1.7

# ---------- Stage 1: build com uv ----------
FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# Resolve dependências primeiro (cache de camada)
COPY pyproject.toml ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev --no-install-project

# Copia o código e instala o projeto
COPY main.py ./
COPY server ./server
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev


# ---------- Stage 2: runtime enxuto ----------
FROM python:3.14-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    MCP_TRANSPORT=sse \
    MCP_HOST=0.0.0.0 \
    MCP_PORT=8080

WORKDIR /app

# Usuário não-root
RUN groupadd --system app && useradd --system --gid app --home /app app

COPY --from=builder --chown=app:app /app /app

USER app

EXPOSE 8080

CMD ["python", "main.py"]
