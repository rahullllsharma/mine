"""critical_field_activity_description
Revision ID: 6a4efa57c230
Revises: 94365d01a5bd
Create Date: 2023-10-18 17:20:18.559034
"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

revision = "6a4efa57c230"
down_revision = "94365d01a5bd"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "activities",
        sa.Column(
            "is_critical", sa.Boolean(), server_default=sa.false(), nullable=False
        ),
    )
    op.add_column(
        "activities",
        sa.Column(
            "critical_description", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
    )


def downgrade():
    op.drop_column("activities", "critical_description")
    op.drop_column("activities", "is_critical")
