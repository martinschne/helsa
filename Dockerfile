# base build
FROM python:3.13-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --no-compile --upgrade -r requirements.txt
COPY /app ./app
COPY .env ./.env
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /code
USER appuser

# development build (incl. debugging)
FROM base AS dev
# EXPOSE 8000
# EXPOSE 5678
RUN pip install --no-cache-dir --no-compile --upgrade debugpy
CMD ["python", "-m", "debugpy", "--listen",  "0.0.0.0:5678", "-m", "fastapi", "run", "/code/app/main.py", "--port", "8000"]

# production build
FROM base AS prod
# EXPOSE 8000
CMD ["fastapi", "run", "/code/app/main.py", "--port", "8000"]