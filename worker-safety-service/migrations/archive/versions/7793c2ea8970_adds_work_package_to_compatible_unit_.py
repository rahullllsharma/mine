"""adds work package to compatible unit table

Revision ID: 7793c2ea8970
Revises: c13383525e19
Create Date: 2022-11-08 20:24:29.469849

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "7793c2ea8970"
down_revision = "e38a929a5408"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "ingest_work_package_to_compatible_unit_link",
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column(
            "work_package_external_key",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=False,
        ),
        sa.Column(
            "compatible_unit_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
        sa.Column("tenant_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("ingest_work_package_to_compatible_unit_link")
