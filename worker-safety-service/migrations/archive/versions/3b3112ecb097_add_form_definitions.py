"""add form definitions

Revision ID: 3b3112ecb097
Revises: 8b21b0692c70
Create Date: 2023-03-15 15:55:18.244951

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

from worker_safety_service.models.utils import EnumValues

# revision identifiers, used by Alembic.
revision = "3b3112ecb097"
down_revision = "8b21b0692c70"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "form_definitions",
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column(
            "status",
            EnumValues("active", "inactive", name="formdefinitionstatus"),
            nullable=False,
        ),
        sa.Column("external_key", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("tenant_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "form_definitions_tenant_id_ix", "form_definitions", ["tenant_id"], unique=False
    )


def downgrade():
    op.drop_index("form_definitions_tenant_id_ix", table_name="form_definitions")
    op.drop_table("form_definitions")
