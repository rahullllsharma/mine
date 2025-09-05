import typer

from worker_safety_service.cli.utils import TyperContext, run_async, with_session
from worker_safety_service.dal.supervisors import SupervisorsManager
from worker_safety_service.dal.user import UserManager
from worker_safety_service.models import User

app = typer.Typer()


@app.callback()
@run_async
@with_session
async def get_user(
    ctx: TyperContext,
    email: str = typer.Option(..., "-e", help="User's email address"),
) -> None:
    user_manager = UserManager(ctx.session)
    user = await user_manager.get_by_email(email=email)

    if user is None:
        typer.echo(f"User not found for email: {email}")
        raise typer.Exit()

    ctx.ensure_object(dict)
    ctx.obj["user"] = user


@app.command(name="as-supervisor")
@run_async
@with_session
async def set_user_as_supervisor(
    ctx: TyperContext,
    supervisor_id: str = typer.Argument(..., help="The user's supervisor id"),
    force: bool = typer.Option(False, help="If set also creates the supervisor"),
) -> None:
    user: User = ctx.obj["user"]
    if user is None:
        typer.echo("User not found")
        raise typer.Exit()

    supervisor_manager = SupervisorsManager(ctx.session)
    supervisor = await supervisor_manager.get_supervisors_by_external_key(supervisor_id)

    if supervisor is not None:
        if force:
            typer.echo(
                f"Supervisor already exists for id {supervisor_id}. Please run again without --force."
            )
            raise typer.Exit()
    elif force:
        supervisor = await supervisor_manager.create_supervisor(supervisor_id)  # type: ignore
    else:
        typer.echo(
            f"Supervisor not found for id {supervisor_id}. Run again with --force to also create the supervisor."
        )
        raise typer.Exit()

    supervisor = await supervisor_manager.set_supervisor_user(supervisor, user)
    typer.echo(f"User set as supervisor with id: {supervisor.id}")
