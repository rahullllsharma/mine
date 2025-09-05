# base image - debian & python 3
FROM --platform=linux/amd64 python:3.10.0-slim as base

ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1 \
    VENV_PATH=/venv

WORKDIR /app


# create virtualenv with dependencies
FROM base as builder

RUN apt-get update && apt-get install -y gcc curl

ENV pip_default_timeout=100 \
    pip_disable_pip_version_check=1 \
    pip_no_cache_dir=1 \
    POETRY_VIRTUALENVS_CREATE=false

RUN curl -sSL https://install.python-poetry.org | python -
ENV PATH="/root/.local/bin:$PATH"
RUN python -m venv ${VENV_PATH}
COPY pyproject.toml poetry.lock ./
SHELL ["/bin/bash", "-c"]
RUN source ${VENV_PATH}/bin/activate && poetry install --only main


# copy built packages into clean image
FROM base as final

ARG APP_COMMIT_SHA=unknown
ENV APP_COMMIT_SHA=${APP_COMMIT_SHA}

COPY --from=builder ${VENV_PATH} ${VENV_PATH}
COPY pyproject.toml ./pyproject.toml
COPY worker_safety_service ./worker_safety_service
COPY alembic.ini ./alembic.ini
COPY migrations ./migrations

RUN ln -s ${VENV_PATH}/bin/alembic /usr/local/bin/alembic

ENTRYPOINT ["alembic"]
