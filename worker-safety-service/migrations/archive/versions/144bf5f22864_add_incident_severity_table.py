"""add-Incident-Severity-table

Revision ID: 144bf5f22864
Revises: 3319de526123
Create Date: 2023-01-31 14:47:34.984310

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "144bf5f22864"
down_revision = "caf177884998"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "incident_severities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("weight", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column("incidents", sa.Column("severity_id", sa.Integer(), nullable=True))
    op.create_index(
        "incidents_severity_id_ix", "incidents", ["severity_id"], unique=False
    )
    op.create_foreign_key(
        "incidents_severity_id_fk",
        "incidents",
        "incident_severities",
        ["severity_id"],
        ["id"],
    )


def downgrade():
    op.drop_constraint("incidents_severity_id_fk", "incidents", type_="foreignkey")
    op.drop_index("incidents_severity_id_ix", table_name="incidents")
    op.drop_column("incidents", "severity_id")
    op.drop_table("incident_severities")
