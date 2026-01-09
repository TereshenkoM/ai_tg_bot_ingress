# syntax=docker/dockerfile:1.7

FROM python:3.14-rc-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    UV_NO_PROGRESS=1 \
    UV_CACHE_DIR=/tmp/uv-cache \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      ca-certificates curl \
      git openssh-client \
 && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /root/.ssh \
 && ssh-keyscan github.com >> /etc/ssh/ssh_known_hosts

RUN ln -sf /usr/local/bin/python3 /usr/local/bin/python

RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
 && if [ -x /root/.local/bin/uv ]; then cp /root/.local/bin/uv /usr/local/bin/uv; \
    elif [ -x /root/.cargo/bin/uv ]; then cp /root/.cargo/bin/uv /usr/local/bin/uv; \
    else echo "uv binary not found after install" && exit 1; fi \
 && chmod 0755 /usr/local/bin/uv \
 && uv --version

WORKDIR /app

COPY pyproject.toml uv.lock /app/

RUN uv venv /opt/venv \
 && /opt/venv/bin/python -m ensurepip --upgrade \
 && /opt/venv/bin/python -m pip install --no-cache-dir --upgrade pip setuptools wheel

RUN --mount=type=ssh uv sync --frozen --no-dev

COPY . /app



FROM python:3.14-rc-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

RUN apt-get update \
 && apt-get install -y --no-install-recommends tini ca-certificates \
 && rm -rf /var/lib/apt/lists/*

RUN ln -sf /usr/local/bin/python3 /usr/local/bin/python

RUN useradd -m -u 10001 -s /usr/sbin/nologin appuser

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app /app

RUN chown -R appuser:appuser /app

USER appuser

RUN python -c "import aiogram, celery, redis, httpx; print('deps ok')" \
 && python -c "import logger; print('logger ok:', logger.__file__)"

ENTRYPOINT ["tini", "--"]
CMD ["python", "main.py"]
