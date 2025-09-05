"""create_compatible_unit_and_elements_models

Revision ID: e47146dcdd71
Revises: afb1e5339081
Create Date: 2022-11-18 12:49:10.191519

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "e47146dcdd71"
down_revision = "afb1e5339081"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "elements",
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", name="elements_name_key"),
    )
    op.create_table(
        "compatible_units",
        sa.Column(
            "compatible_unit_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
        sa.Column("tenant_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("element_name", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.ForeignKeyConstraint(
            ["element_name"],
            ["elements.name"],
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
        ),
        sa.PrimaryKeyConstraint("compatible_unit_id", "tenant_id"),
    )
    op.create_table(
        "element_task_link",
        sa.Column("element_name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("task_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["element_name"],
            ["elements.name"],
        ),
        sa.ForeignKeyConstraint(
            ["task_id"],
            ["tasks.id"],
        ),
        sa.PrimaryKeyConstraint("element_name", "task_id"),
    )
    op.drop_constraint(
        "ingest_work_package_to_compatible_unit_link_tenant_id_fkey",
        "ingest_work_package_to_compatible_unit_link",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "fk_compatible_unit_id_tenant_id",
        "ingest_work_package_to_compatible_unit_link",
        "compatible_units",
        ["compatible_unit_id", "tenant_id"],
        ["compatible_unit_id", "tenant_id"],
    )
    op.alter_column(
        "ingestion_process",
        "submitted_at",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        nullable=True,
    )


def downgrade():
    op.alter_column(
        "ingestion_process",
        "submitted_at",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        nullable=False,
    )
    op.drop_constraint(
        "fk_compatible_unit_id_tenant_id",
        "ingest_work_package_to_compatible_unit_link",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "ingest_work_package_to_compatible_unit_link_tenant_id_fkey",
        "ingest_work_package_to_compatible_unit_link",
        "tenants",
        ["tenant_id"],
        ["id"],
    )
    op.drop_table("element_task_link")
    op.drop_table("compatible_units")
    op.drop_table("elements")
