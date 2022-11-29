FROM python:3.9 AS base
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
RUN apt-get update && \
    pip install --upgrade pip && \
    pip install poetry
WORKDIR /code
COPY pyproject.toml poetry.lock /code/

# =============================================================================

FROM base AS development
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi
COPY . /code/
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# =============================================================================

FROM base AS production
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi
COPY . /code/
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
