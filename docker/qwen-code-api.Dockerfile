# Adapted from qwen-code-api/Dockerfile so the main repository can carry
# deployment-specific overrides without requiring a separate submodule fork.

ARG REGISTRY_PREFIX_DOCKER_HUB
FROM ${REGISTRY_PREFIX_DOCKER_HUB}astral/uv:python3.14-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

COPY qwen-code-api/pyproject.toml qwen-code-api/uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

COPY qwen-code-api/qwen_code_api/ ./qwen_code_api/
COPY qwen-code-api-overrides/qwen_code_api/auth.py ./qwen_code_api/auth.py

ARG REGISTRY_PREFIX_DOCKER_HUB
FROM ${REGISTRY_PREFIX_DOCKER_HUB}python:3.14.2-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends gosu && rm -rf /var/lib/apt/lists/*

RUN groupadd --system --gid 999 nonroot \
    && useradd --system --gid 999 --uid 999 --create-home nonroot

COPY --from=builder --chown=nonroot:nonroot /app /app

RUN mkdir -p /home/nonroot/.qwen && chown nonroot:nonroot /home/nonroot/.qwen

ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY qwen-code-api/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT:-8080}/health')" || exit 1

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["python", "-m", "qwen_code_api.main"]
