FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    AYD_PORT=9000 \
    AYD_THREADS=8

WORKDIR /app

RUN addgroup --system ayd && adduser --system --ingroup ayd --home /app ayd

COPY requirements.txt ./
RUN python -m pip install --upgrade pip && python -m pip install -r requirements.txt

COPY . .
RUN mkdir -p /app/data /app/static/uploads/doubts /app/static/uploads/resources /app/static/qr /app/static/brand /app/exports \
    && chown -R ayd:ayd /app

USER ayd
EXPOSE 9000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD python -c "import os,urllib.request; urllib.request.urlopen('http://127.0.0.1:'+os.getenv('AYD_PORT','9000')+'/healthz', timeout=3).read()" || exit 1

CMD ["sh", "-c", "waitress-serve --listen=0.0.0.0:${AYD_PORT:-9000} --threads=${AYD_THREADS:-8} app:app"]
