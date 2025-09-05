import csv
import json

import httpx
import typer

from worker_safety_service.cli.utils import TyperContext, run_async

app = typer.Typer()

client = httpx.AsyncClient()


@app.command(name="add")
@run_async
async def add_incidents(
    ctx: TyperContext,
    csv_file: typer.FileText,
    jwt: str = typer.Argument("", envvar="JWT", show_envvar=False),
    base_url: str = "http://localhost:8000/rest",
    delimiter: str = ",",
) -> None:
    """Add incidents to worker safety
    requires exporting a JWT into the environment: `export JWT=...`
    """
    assert jwt

    async def create_incidents(incidents: list[dict]) -> None:
        data = {
            "data": [
                {"type": "incident", "attributes": {k: v for k, v in i.items() if v}}
                for i in incidents
            ]
        }

        headers = {"Authorization": f"Bearer {jwt}"}
        # fastapi seems to require a json blob as the `data` argument instead of a python object
        response = await client.post(
            f"{base_url}/incidents/bulk",
            headers=headers,
            data=json.dumps(data),  # type:ignore
        )
        assert response.status_code == 201
        typer.echo(f"added {len(incidents)} records")

    data = csv.DictReader(csv_file, delimiter=delimiter)
    collection = []
    for row in data:
        collection.append(row)
        if len(collection) == 100:
            await create_incidents(collection)
            collection = []
    if collection:
        await create_incidents(collection)
