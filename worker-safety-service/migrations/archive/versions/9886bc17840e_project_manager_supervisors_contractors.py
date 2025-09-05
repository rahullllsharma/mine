"""Project manager, supervisors, contractors

Revision ID: 9886bc17840e
Revises: fd680fdd0a2c
Create Date: 2022-02-14 22:26:31.802651

"""
import uuid

import sqlalchemy as sa
import sqlmodel
from alembic import op
from sqlalchemy import text
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "9886bc17840e"
down_revision = "fd680fdd0a2c"
branch_labels = None
depends_on = None


def upgrade():
    with_projects = op.get_bind().execute("SELECT id FROM projects LIMIT 1").first()

    op.add_column(
        "projects",
        sa.Column("manager_id", sqlmodel.sql.sqltypes.GUID(), nullable=with_projects),
    )
    op.add_column(
        "projects",
        sa.Column(
            "supervisor_id", sqlmodel.sql.sqltypes.GUID(), nullable=with_projects
        ),
    )
    op.add_column(
        "projects",
        sa.Column(
            "additional_supervisor_ids",
            sa.ARRAY(postgresql.UUID(as_uuid=True)),
            nullable=with_projects,
        ),
    )
    op.add_column(
        "projects",
        sa.Column(
            "contractor_id", sqlmodel.sql.sqltypes.GUID(), nullable=with_projects
        ),
    )

    if with_projects:
        first_user = op.get_bind().execute(text("SELECT id FROM users LIMIT 1")).first()
        if first_user:
            first_user_id = first_user.id
        else:
            first_user_id = uuid.uuid4()
            op.get_bind().execute(
                f"INSERT INTO users (id, keycloak_id, first_name, last_name) VALUES('{first_user_id}'::uuid, '{uuid.uuid4()}'::uuid, 'Undefined', '');"
            )

        # We have data, added by revision 254ce3767087
        first_contractor_id = (
            op.get_bind().execute("SELECT id FROM contractor LIMIT 1").first()[0]
        )

        op.execute(f"UPDATE projects SET manager_id = '{first_user_id}'")
        op.alter_column("projects", "manager_id", nullable=False)

        op.execute(f"UPDATE projects SET supervisor_id = '{first_user_id}'")
        op.alter_column("projects", "supervisor_id", nullable=False)

        op.execute("UPDATE projects SET additional_supervisor_ids = '{}'")
        op.alter_column("projects", "additional_supervisor_ids", nullable=False)

        op.execute(f"UPDATE projects SET contractor_id = '{first_contractor_id}'")
        op.alter_column("projects", "contractor_id", nullable=False)

    op.create_foreign_key(
        "projects_supervisor_id_fkey", "projects", "users", ["supervisor_id"], ["id"]
    )
    op.create_foreign_key(
        "projects_manager_id_fkey", "projects", "users", ["manager_id"], ["id"]
    )
    op.create_foreign_key(
        "projects_contractor_id_fkey",
        "projects",
        "contractor",
        ["contractor_id"],
        ["id"],
    )


def downgrade():
    op.drop_column("projects", "contractor_id")
    op.drop_column("projects", "additional_supervisor_ids")
    op.drop_column("projects", "supervisor_id")
    op.drop_column("projects", "manager_id")
