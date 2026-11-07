FROM python:3.13-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt


ENV TIKTOKEN_CACHE_DIR=/opt/tiktoken
RUN python -c "import tiktoken; tiktoken.get_encoding('gpt2')"


FROM python:3.13-slim AS runtime

RUN apt-get update \
    && apt-get install -y --no-install-recommends libmagic1 \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --uid 1000 app

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /opt/tiktoken /opt/tiktoken

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TIKTOKEN_CACHE_DIR=/opt/tiktoken \
    # Ollama runs on the host machine. Override for Linux or a remote Ollama or whatever you want.
    OLLAMA_HOST=http://host.docker.internal:11434

WORKDIR /app

# Only the code the API needs. ingestion.py is imported by graph/nodes/retrieve.py.
COPY --chown=app:app config/ config/
COPY --chown=app:app graph/ graph/
COPY --chown=app:app backend/ backend/
COPY --chown=app:app ingestion.py .

RUN mkdir -p /app/.chroma && chown -R app:app /app

USER app

EXPOSE 8005

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8005/v1/health')" || exit 1

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8005"]
