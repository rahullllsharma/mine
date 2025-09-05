# ws-customizable-workflow

## Requirements

- Python (3.12.0)
- [Poetry](https://python-poetry.org/)
- [Docker](https://docker.com)
- Docker Compose
- MongoDB

## Quick Start

### Clone the repo

```shell
git clone https://github.com/urbint/ws-customizable-workflow.git
cd ws-customizable-workflow
```

### Run the App and backing services

```shell
docker-compose up

# on M1 macs - you may need to disable buildkit
# https://urbint.atlassian.net/wiki/spaces/PLAT/pages/3405250567/Local+Dev+on+M1+Mac#Docker-Compose-Execution
DOCKER_BUILDKIT=0 docker-compose up

# on M1 macs, you might also need to comment this line
# in the docker-compose.yml file:
platform: linux/amd64
```

## Development Setup

### Install python dependencies and virtualenv

This project requires Python 3.12.x. We recommend using [`pyenv`](https://github.com/pyenv/pyenv) to manage python versions and [`poetry`](https://python-poetry.org/) for virtual environments and dependencies.

<details>
  <summary>Pyenv install</summary>

```shell
brew install pyenv
# from pyenv github readme under `zsh` setup
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
source ~/.zshrc

# install python 3.12.0
pyenv install 3.12.0

# Set local version
pyenv local 3.12.0
```

</details>

<details>
  <summary>Poetry install</summary>

brew install poetry

</details>

```shell
poetry install
```

### Setup autohooks

Autohooks is a Python library that assists in automated formatting and linting using Black and Pylint during git commits. This feature aids in identifying and addressing linting and typing issues in code before committing, thereby minimizing build pipeline failures resulting from such issues.

For further details on Autohooks, please refer to this URL: https://pypi.org/project/autohooks/

Autohooks utilizes the setup.cfg file to configure details for various libraries such as isort, flake8, and mypy. The settings for Autohooks are specified in the pyproject.toml file.

Run the following command to activate autohooks after the `poetry install` command:

```shell
poetry run autohooks activate --mode poetry
```

### Start the application

#### Rest API

Need to have a running mongo instance before the application starts up. You can start the mongodb service externally or use docker-compose, like `docker-compose up [-d] mongodb`

```shell
poetry run uvicorn --reload ws_customizable_workflow.main:app
```

## Continuous Integration

This repository uses GitHub Actions as a continuous integration (CI) system to automate the process of checking the quality of our code.

Read more about our CI process [here](docs/github-actions.md).
