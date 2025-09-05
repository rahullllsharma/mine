"""contractor-alias-tenant

Revision ID: 16dea8b8b9c3
Revises: 69c7656bd2ea
Create Date: 2022-04-06 17:15:48.975649

"""
import uuid

from alembic import op
from sqlmodel import Session

# revision identifiers, used by Alembic.
revision = "16dea8b8b9c3"
down_revision = "26276323d067"
branch_labels = None
depends_on = None


def upgrade():
    # make contractor tenant_id nullable?
    op.execute("alter table contractor alter column tenant_id drop not NULL;")

    # add tenant_id to contractor_alias as nullable FK
    op.execute("alter table contractor_aliases add column tenant_id UUID;")
    op.execute(
        "alter table contractor_aliases add constraint contractor_aliases_tenant_id_fkey FOREIGN KEY(tenant_id) references tenants(id);"
    )
    # drop unique constraint on alias
    op.execute(
        "alter table contractor_aliases drop constraint contractor_aliases_alias_key;"
    )
    op.execute(" alter table contractor_aliases add column id UUID;")

    with Session(bind=op.get_bind()) as session:
        for alias in session.execute("select * from contractor_aliases;"):
            update = f"update contractor_aliases set id='{uuid.uuid4()}' where  alias='{alias.alias}';"
            session.execute(update)
            session.commit()

    op.execute(
        "alter table contractor_aliases add constraint contractor_aliases_pkey PRIMARY KEY(id);"
    )
    op.execute("alter table contractor_aliases alter column alias drop not NULL;")


def downgrade():
    op.execute("delete from contractor where tenant_id = NULL;")
    op.execute("alter table contractor alter column tenant_id set not NULL;")
    op.execute("alter table contractor_aliases drop column tenant_id cascade;")
    op.execute(
        "alter table contractor_aliases add constraint contractor_aliases_alias_key UNIQUE(alias);"
    )
    op.execute("alter table contractor_aliases drop column id cascade;")
    op.execute("alter table contractor_aliases alter column alias set not NULL;")
