FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY docker/requirements-inference.txt ./docker/requirements-inference.txt
RUN pip install --no-cache-dir -r docker/requirements-inference.txt
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir --no-deps --no-build-isolation . \
    && useradd --create-home --uid 10001 appuser

USER appuser
EXPOSE 8000
CMD ["uvicorn", "claims_intelligence.serving.api:app", "--host", "0.0.0.0", "--port", "8000"]
