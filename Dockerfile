# Non-model API image for reproducible dependency and startup smoke.
# Does not bake model weights. Do not use this image as Windows acceptance evidence.
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DOTENV_PATH=/app/backend/docker-smoke.env \
    WARMUP_MODELS=0

RUN apt-get update \
    && apt-get install -y --no-install-recommends git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend/requirements.txt backend/constraints.txt ./backend/

# CPU torch first so pip does not resolve multi-GB CUDA wheels, then the pinned tree.
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir \
        --index-url https://download.pytorch.org/whl/cpu \
        "torch==2.9.1" "torchvision==0.24.1" \
    && pip install --no-cache-dir \
        -c backend/constraints.txt \
        -r backend/requirements.txt

COPY backend/app ./backend/app
COPY backend/worker ./backend/worker
COPY backend/inference ./backend/inference
COPY backend/tests ./backend/tests
COPY backend/docker-smoke.env ./backend/docker-smoke.env

WORKDIR /app/backend
EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
