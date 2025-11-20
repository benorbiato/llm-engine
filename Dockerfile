FROM python:3.11-slim as builder

WORKDIR /src

RUN apt-get update && \ 
    apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libpq-dev \
    libssl-dev \
    libffi-dev \
    zlib1g-dev \
    gcc \
    g++ \
    make \
    curl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim

LABEL maintainer="norbiato.dev@gmail.com"
LABEL description="LLM Engine"
LABEL version="1.0.0"

WORKDIR /src

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

COPY ./src /src/src

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /src
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/v1/health || exit 1

CMD ["python", "-m", "uvicorn", "src.entrypoints.main_api:app", "--host", "0.0.0.0", "--port", "8000"]