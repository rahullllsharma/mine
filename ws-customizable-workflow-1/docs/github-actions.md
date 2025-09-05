# GitHub Actions Workflows
This repository uses GitHub Actions as a continuous integration (CI) system to automate the process of checking the quality of our code.

## Linting and Type Checking Workflow
We have defined a workflow in the `lint.yml` file that runs four different linting tools: `black`, `flake8`, `isort`, and `mypy`.

### Workflow Triggers
The workflow is triggered whenever code is pushed to any branch in the repository.

### Jobs
The workflow consists of several jobs:

- `black`: This job checks that our Python code adheres to the Black code style.
- `flake8`: This job uses Flake8 to catch common Python errors and enforce a subset of PEP 8, the Python style guide.
- `isort`: This job checks that our Python imports are sorted alphabetically and separated into sections as per the isort tool.
- `mypy`: This job uses Mypy, a static type checker for Python, to catch potential bugs in our code.

## Run Tests Workflow

We have also defined a workflow in the `run-tests.yml` file that runs our unit tests. This workflow is crucial to ensure that all the functionalities of our code are working as expected.

### Workflow Triggers

The workflow is triggered whenever code is pushed to any branch in the repository, or when a pull request is made against the `main` branch.

### Jobs

The workflow consists of one job:

- `run-tests`: This job runs all the unit tests in our codebase using the  `pytest`. If any test fails, the workflow will fail, indicating that there are issues that need to be addressed.

## Build and Push Docker Image Workflow

We have a workflow defined in the `build-and-push-docker-image.yml` file that builds a Docker image from our code and pushes it to a Docker registry. This workflow is essential for deploying our application.

### Workflow Triggers

This workflow is triggered whenever the `Run Tests` workflow has completed successfully. 

### Jobs

The workflow consists of one job:

- `build-and-push`: This job builds a Docker image from our Dockerfile, tags it with the Git tag that triggered the workflow, and pushes it to our Docker registry.

## Conclusion
By using GitHub Actions, we can ensure that all code in the repository meets our quality standards before it is merged. This helps us maintain a high-quality codebase and catch potential issues early in the development process.