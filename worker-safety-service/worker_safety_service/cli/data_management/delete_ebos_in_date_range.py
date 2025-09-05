import datetime
import uuid
from typing import Optional

import sqlalchemy as sa
import typer

from worker_safety_service.cli.utils import TyperContext, run_async, with_session

app = typer.Typer()


@app.command("delete_ebos")
@run_async
@with_session
async def delete_ebos_in_date_range(
    ctx: TyperContext,
    tenant_id: uuid.UUID,
    end_date: datetime.datetime,
    start_date: Optional[datetime.datetime] = None,
) -> None:
    if start_date is None:
        await ctx.session.execute(
            sa.text(
                f"DELETE FROM energy_based_observations WHERE created_at <= '{end_date}' AND tenant_id = '{tenant_id}'"
            )
        )
        undeleted_records = (
            await ctx.session.execute(
                sa.text(
                    f"SELECT * FROM energy_based_observations WHERE created_at <= '{end_date}' AND tenant_id = '{tenant_id}'"
                )
            )
        ).all()

        if len(undeleted_records) != 0:
            await ctx.session.rollback()
        else:
            typer.echo(
                f"Deleting EBOs for tenant_id={tenant_id}, between start_date={start_date} and end_date={end_date}"
            )
    else:
        await ctx.session.execute(
            sa.text(
                f"DELETE FROM energy_based_observations WHERE created_at >= '{start_date}' AND created_at <= '{end_date}' AND tenant_id = '{tenant_id}'"
            )
        )
        undeleted_records = (
            await ctx.session.execute(
                sa.text(
                    f"SELECT * FROM energy_based_observations WHERE created_at >= '{start_date}' AND created_at <= '{end_date}' AND tenant_id = '{tenant_id}'"
                )
            )
        ).all()

        if len(undeleted_records) != 0:
            await ctx.session.rollback()
        else:
            typer.echo(
                f"Deleting EBOs for tenant_id={tenant_id}, between start_date={start_date} and end_date={end_date}"
            )

    await ctx.session.commit()
