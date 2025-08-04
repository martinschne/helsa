# base build
FROM python:3.13-slim AS base
COPY --from=ghcr.io/astral-sh/uv:0.8.4 /uv /uvx /bin/
WORKDIR /app
COPY src ./src
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# development build (incl. debugging)
FROM base AS dev
RUN uv pip install debugpy
CMD [".venv/bin/python", "-Xfrozen_modules=off", "-m", "debugpy", "--listen", "0.0.0.0:5678", "-m", "uvicorn", "helsa.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# production build
FROM base AS prod
CMD [".venv/bin/uvicorn", "helsa.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]