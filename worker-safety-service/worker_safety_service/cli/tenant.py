import json
import re

import typer

from worker_safety_service.cli.utils import TyperContext, run_async, with_session
from worker_safety_service.dal.tenant import TenantManager
from worker_safety_service.models import TenantCreate

app = typer.Typer()


@app.command(name="create")
@run_async
@with_session
async def create_tenant(
    ctx: TyperContext,
    name: str = typer.Argument(
        ...,
        help="The suffix that identifies the client subdomain (ex: worker-safety-$SUBDOMAIN-SUFFIX)",
    ),
    display_name: str = typer.Argument(..., help="tenant display name"),
    realm_name: str = typer.Argument(..., help="The keycloak realm name"),
) -> None:
    """
    Create a new tenant with the name equal to the auth_realm_name
    """
    tenant_manager = TenantManager(ctx.session)
    tenant = await tenant_manager.create(
        tenant=TenantCreate(
            tenant_name=name, display_name=display_name, auth_realm_name=realm_name
        )
    )
    typer.echo(json.dumps(json.loads(tenant.json()), indent=4, sort_keys=True))


@app.command(name="select")
@run_async
@with_session
async def select_tenants(
    ctx: TyperContext,
    name: str = typer.Argument(..., help="The name of the tenant (or part of it)"),
) -> None:
    """
    Find tenant(s) by name
    """
    tenant_manager = TenantManager(ctx.session)
    tenants = await tenant_manager.find_tenants_by_partial_name(name)
    for tenant in tenants:
        typer.echo(json.dumps(json.loads(tenant.json()), indent=4, sort_keys=True))


@app.command(name="list")
@run_async
@with_session
async def list_tenants(ctx: TyperContext) -> None:
    """
    List all tenants
    """
    tenant_manager = TenantManager(ctx.session)
    tenants = await tenant_manager.get_tenants()
    for tenant in tenants:
        typer.echo(json.dumps(json.loads(tenant.json()), indent=4, sort_keys=True))


@app.command(name="new-realm")
@run_async
async def new_realm(
    ctx: TyperContext,
    name: str = typer.Argument(..., help="Internal keycloak name for the new realm"),
    display_name: str = typer.Argument(..., help="Display name for the new realm"),
    url: str = typer.Argument(..., help="Tenant URL (exclude trailing slash)"),
) -> None:
    """
    Generate import file to create a new realm in keycloak.
    """

    # To update the template from an existing keycloak realm
    # export the realm as json
    # remove all lines containing a UUID
    # remove private key data
    # and replace references to the realm name, display name, and url with template keys
    template = open("worker_safety_service/cli/tenant.template").read()

    # ensure template does not include references to unique (ie: existing) resources
    unique_ids = {
        i.group()
        for i in re.finditer(
            "[a-fA-F0-9]{8}-([a-fA-F0-9]{4}-){3}[a-fA-F0-9]{12}", template
        )
    }
    assert len(unique_ids) == 0

    template = template.replace("{{name}}", name)
    template = template.replace("{{display_name}}", display_name)
    template = template.replace("{{url}}", url)
    print(template)
