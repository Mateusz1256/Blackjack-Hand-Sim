FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    BLACKJACK_API_HOST=0.0.0.0 \
    BLACKJACK_API_PORT=8000 \
    BLACKJACK_API_ENVIRONMENT=compose \
    BLACKJACK_API_DATABASE_PATH=/data/blackjack_api.sqlite3

WORKDIR /app

RUN addgroup --system blackjack \
    && adduser --system --ingroup blackjack blackjack \
    && mkdir -p /data \
    && chown blackjack:blackjack /data

COPY pyproject.toml README.md LICENSE ./
COPY src ./src
COPY backend/src ./backend/src

RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir .

USER blackjack
EXPOSE 8000
VOLUME ["/data"]

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import json, urllib.request; data=json.load(urllib.request.urlopen('http://127.0.0.1:8000/api/v1/health', timeout=3)); raise SystemExit(0 if data.get('status') == 'ok' else 1)"

CMD ["python", "-m", "uvicorn", "blackjack_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
