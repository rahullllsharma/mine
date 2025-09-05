"""add crew_leader table

Revision ID: f6162f29f8c9
Revises: 1c6650ce09c7
Create Date: 2023-11-06 13:00:05.123382

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "f6162f29f8c9"
down_revision = "1c6650ce09c7"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "crew_leader",
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("tenant_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("idx_crew_leader_tenant_id"), "crew_leader", ["tenant_id"], unique=False
    )


def downgrade():
    op.drop_index(op.f("idx_crew_leader_tenant_id"), table_name="crew_leader")
    op.drop_table("crew_leader")
