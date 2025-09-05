import typer

from worker_safety_service.rest import openapi
from worker_safety_service.rest.routers import OpenapiSpecRouters

app = typer.Typer()

OUTPUT_FILE = typer.Option(
    None,
    "--output-file",
    "-o",
    help="write to this file",
)
LIMIT = typer.Option(
    None,
    "--limit",
    "-l",
    help="Select specific routers to include in the spec. Defaults to all routers",
)


@app.command()
def current(
    output_file: typer.FileTextWrite = OUTPUT_FILE,
    limit: list[OpenapiSpecRouters] = LIMIT,
) -> None:
    """Get the current Rest-API specification file"""

    spec = openapi.current(limit=limit)
    if output_file:
        output_file.write(spec)
    else:
        typer.echo(spec)
