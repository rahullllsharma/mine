# Use the official Python image with slim variant
FROM python:3.12.0-slim AS base

# Set environment variables
ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1 \
    VENV_PATH=/venv

# Set the working directory
WORKDIR /app


FROM base AS builder
# Install system dependencies
RUN apt-get update && apt-get install pipx -y

# Install Poetry
RUN pipx install poetry==1.7.1
ENV PATH="/root/.local/bin:$PATH"
RUN python -m venv ${VENV_PATH}
# Copy only the necessary files for dependency installation
COPY pyproject.toml poetry.lock ./
COPY . ./
RUN . ${VENV_PATH}/bin/activate &&  poetry install --only main


FROM base AS runtime
# Copy the application code
COPY --from=builder ${VENV_PATH} ${VENV_PATH}
COPY pyproject.toml ./pyproject.toml
COPY ws_customizable_workflow ./ws_customizable_workflow
COPY support/uvicorn/mute.logging.conf ./uvicorn.logging.conf

# Install only the required libraries
RUN apt-get -y update \
    && apt-get install -y --no-install-recommends \
    libpango-1.0-0 libpangoft2-1.0-0 \
    && apt-get -y clean \
    && rm -rf /var/lib/apt/lists/*

RUN ln -s ${VENV_PATH}/bin/uvicorn /usr/local/bin/uvicorn
EXPOSE 5001
# TODO: need to understand what the uvicon logging does and what is mute logging
# CMD uvicorn --log-config uvicorn.logging.conf --no-access-log --port=8001 --host=0.0.0.0 ws_customizable_workflow.main:app

# # Command to run the application using Uvicorn
CMD ["uvicorn", "--reload", "ws_customizable_workflow.main:app", "--host", "127.0.0.1", "--port", "5001"]

FROM runtime AS uvicorn
ENTRYPOINT ["uvicorn", "--host=0.0.0.0"]
