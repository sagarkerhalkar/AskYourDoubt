# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.14
FROM python:${PYTHON_VERSION}-slim

ARG APP_VERSION=1.3-light-3d

LABEL org.opencontainers.image.title="AskYourDoubt"
LABEL org.opencontainers.image.description="Live classroom doubt, voting, resource, question-bank and analytics platform"
LABEL org.opencontainers.image.version="${APP_VERSION}"
LABEL org.opencontainers.image.authors="AskYourDoubt"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    AYD_DATABASE=/app/data/database.db \
    AYD_BASE_URL=http://127.0.0.1:9000

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt

COPY . .

RUN groupadd --gid 10001 appgroup \
    && useradd --uid 10001 --gid appgroup --create-home --shell /usr/sbin/nologin appuser \
    && mkdir -p \
        /app/data \
        /app/static/uploads/doubts \
        /app/static/uploads/resources \
        /app/static/qr \
        /app/static/brand \
        /app/exports \
    && chown -R appuser:appgroup /app

USER appuser

EXPOSE 9000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:9000/healthz', timeout=4).read()" || exit 1

STOPSIGNAL SIGTERM

CMD ["python", "-m", "waitress", "--listen=0.0.0.0:9000", "--threads=8", "app:app"]
