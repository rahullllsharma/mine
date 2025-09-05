"""Add EBO table

Revision ID: a8886780aae1
Revises: 0c2a36b3ea1a
Create Date: 2023-07-28 15:23:48.039757

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "a8886780aae1"
down_revision = "0c2a36b3ea1a"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "energy_based_observations",
        sa.Column("date_for", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("contents", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("tenant_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("created_by_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("completed_by_id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["completed_by_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["created_by_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.execute(
        "ALTER TABLE energy_based_observations ADD COLUMN status form_status NOT NULL;"
    )

    op.alter_column("jsbs", "date_for", type_=sa.Date(), nullable=False)


def downgrade():
    op.drop_table("energy_based_observations")
