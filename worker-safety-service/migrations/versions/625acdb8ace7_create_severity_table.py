"""create severity table

Revision ID: 625acdb8ace7
Revises: eb9a950d1437
Create Date: 2024-01-02 11:35:25.476687

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "625acdb8ace7"
down_revision = "eb9a950d1437"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "incident_severities",
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("ui_label", sa.String(254), nullable=False),
        sa.Column("api_value", sa.String(254), nullable=False),
        sa.Column("source", sa.String(254), nullable=False),
        sa.Column("old_severity_mapping", sa.String(254), nullable=True),
        sa.Column("safety_climate_multiplier", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade():
    op.drop_table("incident_severities")
