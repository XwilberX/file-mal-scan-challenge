FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Instalar solo dependencias según uv.lock y pyproject.toml
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Añadir código fuente y sincronizar proyecto
ADD . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

FROM python:3.12-slim-bookworm AS final

# Runtime: librerías mínimas necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    netcat-traditional \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app /app
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH=/app/src

WORKDIR /app
EXPOSE 8080
RUN chmod +x /app/scripts/entrypoint.sh

CMD ["/app/scripts/entrypoint.sh"]
