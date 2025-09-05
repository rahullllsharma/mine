# base image - debian & python 3
FROM python:3.10.10-slim as base

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

# TODO: Perhaps join both images!
# TODO: We should probably fix the poetry version
RUN curl -sSL https://install.python-poetry.org | python -
ENV PATH="/root/.local/bin:$PATH"
RUN python -m venv ${VENV_PATH}
COPY pyproject.toml poetry.lock ./
COPY . ./
RUN . ${VENV_PATH}/bin/activate && poetry install --only main


# copy built packages into clean image
FROM base as runtime

ARG APP_COMMIT_SHA=unknown
ENV APP_COMMIT_SHA=${APP_COMMIT_SHA}

COPY --from=builder ${VENV_PATH} ${VENV_PATH}
COPY pyproject.toml ./pyproject.toml
COPY worker_safety_service ./worker_safety_service
COPY support/uvicorn/mute.logging.conf ./uvicorn.logging.conf

RUN ln -s ${VENV_PATH}/bin/wss /usr/local/bin/wss
RUN ln -s ${VENV_PATH}/bin/uvicorn /usr/local/bin/uvicorn
# Left uvicorn base command for backwards compatibility.
CMD uvicorn --log-config uvicorn.logging.conf --no-access-log --host=0.0.0.0 worker_safety_service.graphql.main:app

FROM runtime as uvicorn
ENTRYPOINT ["uvicorn", "--log-config", "uvicorn.logging.conf", "--no-access-log", "--host=0.0.0.0"]

FROM runtime as migrations

COPY alembic.ini ./alembic.ini
COPY migrations ./migrations

RUN ln -s ${VENV_PATH}/bin/alembic /usr/local/bin/alembic

ENTRYPOINT ["alembic"]