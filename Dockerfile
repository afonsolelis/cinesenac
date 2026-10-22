# Imagem da aplicação (ADR-0019). O segredo entra por variável de ambiente, nunca pela imagem.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    CINESENAC_DATABASE_URL=sqlite:////data/cinesenac.db

WORKDIR /app

RUN pip install --no-cache-dir uv \
    && useradd --create-home --uid 10001 appuser \
    && mkdir -p /data && chown appuser /data

COPY pyproject.toml README.md ./
COPY app ./app
RUN uv pip install --system --no-cache . && rm -rf /app/app /app/pyproject.toml /app/README.md

USER appuser
VOLUME ["/data"]
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=2)"

CMD ["uvicorn", "app.main:criar_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
