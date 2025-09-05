#!/usr/bin/env python3
# (from the repo's root directory)
# poetry run ./support/scripts/dev/main.py
# poetry run dev
# poetry run dev --help

import os
from typing import Any

import typer

app = typer.Typer()


def pr(
    msg: str, *args: Any, prefix: str = "DEV", prefix_color: str = typer.colors.GREEN
) -> None:
    """
    Print a message and it's args. Accepts a prefix that is wrapped in `[<prefix>]`.
    Applies some colors to the first `msg` arg.
    """
    args_str = (
        typer.style(" ".join(map(str, args)), fg=typer.colors.YELLOW) if args else None
    )
    prefix = typer.style(f"[{prefix}]", fg=prefix_color, bold=True)
    msg = typer.style(msg, fg=typer.colors.CYAN)
    if args_str:
        typer.echo(f"{prefix} {msg} {args_str}")
    else:
        typer.echo(f"{prefix} {msg}")


def run_cmd(
    cmd: str,
    message: str = "Running command",
    prefix: str = "DEV",
    exit_on_error: bool = True,
) -> None:
    """
    Helper for running a cli command.
    Typer command even in the case of failure.
    """
    pr(message, cmd, prefix=prefix)
    res = os.system(cmd)
    if res == 0:
        pr("Success", prefix=prefix)
    else:
        pr("Error", prefix=prefix, prefix_color=typer.colors.RED)
        if exit_on_error:
            raise typer.Exit(code=1)


@app.command()
def deps() -> None:
    """
    Installs deps from poetry.
    """
    run_cmd("poetry install", message="Installing deps via poetry", prefix="DEPS")


################################################################################
# Docker


@app.command()
def docker() -> None:
    """
    Starts the usual dev docker containers.
    """
    docker_cmd = "docker-compose up -d rest mongodb"
    run_cmd(docker_cmd, message="Starting up docker containers", prefix="DOCKER")


# TODO: CHECK LOGGER IMPLEMENTATION WITH Aaron.
# @app.command()
# def docker_graphql_log() -> None:
#     """
#     Follows the logs from the graphql app container.
#     """
#     docker_cmd = "docker-compose logs -f graphql"
#     pr("Logging graphql container", docker_cmd, prefix="DOCKER")
#     os.system(docker_cmd)


################################################################################
# Formatting/Linting


@app.command()
def lint(check: bool = False) -> None:
    """
    Runs our auto-formatters, then runs all the linters that CI will run.
    """
    if not check:
        # formatters
        run_cmd("black .", message="Formatting with `black`", prefix="BLACK")
        run_cmd("isort .", message="Formatting with `isort`", prefix="FLAKE8")

    # linters
    run_cmd(
        "black --check .",
        message="Linting with `black`",
        prefix="BLACK",
        exit_on_error=check,
    )
    run_cmd(
        "flake8 .",
        message="Linting with `flake8`",
        prefix="FLAKE8",
        exit_on_error=check,
    )
    run_cmd(
        "isort --check .",
        message="Linting with `isort`",
        prefix="ISORT",
        exit_on_error=check,
    )
    run_cmd(
        "mypy .",
        message="Linting with `mypy`",
        prefix="MYPY",
        exit_on_error=check,
    )


################################################################################
# Tests


@app.command()
def test_unit() -> None:
    """
    Runs the unit tests.
    """
    run_cmd("pytest ./tests/unit", message="Running unit tests", prefix="TEST")


@app.command()
def test_integration() -> None:
    """
    Runs the integration tests.
    """
    # TODO clean up hanging tmpl dbs before running?
    run_cmd(
        "pytest -vv -n auto ./tests/integration",
        message="Running integration tests",
        prefix="TEST",
    )


@app.command()
def test_all() -> None:
    """
    `test-unit` + `test-integration`
    """
    test_unit()
    test_integration()


@app.command()
def test_integration_fail_fast() -> None:
    """
    Runs the integration tests, but exits on the first test failure.
    """
    run_cmd(
        "pytest -x -vv -n auto --maxprocesses=8 ./tests/integration",
        message="Running integration tests (fail fast)",
        prefix="TEST",
    )


@app.command()
def test_match(match_str: str) -> None:
    """
    Runs tests matching the provided match_str.
    """
    run_cmd(
        f"pytest -vv --durations=15 ./tests/integration -k {match_str}",
        message=f"Running tests matching {match_str}",
        prefix="TEST",
    )


################################################################################
# Prep


@app.command()
def prep() -> None:
    """
    `deps` + `docker` + `migrate`.
    """
    deps()
    docker()


################################################################################
# Main


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """
    WS Customizable workflow dev support commands.
    """
    if ctx.invoked_subcommand is None:
        pr("No command specified, running `prep`.")
        prep()


if __name__ == "__main__":
    app()
