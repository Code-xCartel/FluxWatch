# ── Stage 1: dependency export ────────────────────────────────────────────────
# Uses Poetry only to export a plain requirements.txt so the final image
# has no Poetry overhead at all.
FROM python:3.11-slim AS builder

WORKDIR /build

RUN pip install --no-cache-dir poetry==2.1.1 poetry-plugin-export

COPY pyproject.toml poetry.lock ./

# Export only production deps (no dev/test groups)
RUN poetry export --only main --without-hashes --format=requirements.txt \
    -o requirements.txt


# ── Stage 2: production image ─────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install deps from the exported requirements file
COPY --from=builder /build/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY flux_watch_api/ ./flux_watch_api/

# Non-root user for security
RUN adduser --disabled-password --gecos "" appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "flux_watch_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
