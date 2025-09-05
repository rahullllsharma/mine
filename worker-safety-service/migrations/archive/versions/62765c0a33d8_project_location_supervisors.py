"""Project location supervisors

Revision ID: 62765c0a33d8
Revises: d692695d0949
Create Date: 2022-02-15 18:47:59.336249

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op
from sqlalchemy import text
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "62765c0a33d8"
down_revision = "d692695d0949"
branch_labels = None
depends_on = None


def upgrade():
    with_entries = (
        op.get_bind().execute("SELECT id FROM project_locations LIMIT 1").first()
    )

    op.add_column(
        "project_locations",
        sa.Column("supervisor_id", sqlmodel.sql.sqltypes.GUID(), nullable=with_entries),
    )
    op.add_column(
        "project_locations",
        sa.Column(
            "additional_supervisor_ids",
            sa.ARRAY(postgresql.UUID(as_uuid=True)),
            nullable=with_entries,
        ),
    )

    if with_entries:
        first_user_id = (
            op.get_bind().execute(text("SELECT id FROM users LIMIT 1")).first()[0]
        )

        op.execute(f"UPDATE project_locations SET supervisor_id = '{first_user_id}'")
        op.alter_column("project_locations", "supervisor_id", nullable=False)

        op.execute("UPDATE project_locations SET additional_supervisor_ids = '{}'")
        op.alter_column(
            "project_locations", "additional_supervisor_ids", nullable=False
        )

    op.create_foreign_key(
        "project_locations_supervisor_id_fkey",
        "project_locations",
        "users",
        ["supervisor_id"],
        ["id"],
    )


def downgrade():
    op.drop_column("project_locations", "supervisor_id")
    op.drop_column("project_locations", "additional_supervisor_ids")
