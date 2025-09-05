"""Create WorkType model and links to LibraryTask and Tenant models

Revision ID: 275fe2e9e4bc
Revises: 4b2fef494feb
Create Date: 2022-10-06 12:41:10.409624

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "275fe2e9e4bc"
down_revision = "2b50925ddde1"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "work_types",
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "work_type_tenant_link",
        sa.Column("work_type_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("tenant_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
        ),
        sa.ForeignKeyConstraint(
            ["work_type_id"],
            ["work_types.id"],
        ),
        sa.PrimaryKeyConstraint("work_type_id", "tenant_id"),
    )
    op.add_column(
        "library_tasks",
        sa.Column("work_type_id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
    )
    op.create_foreign_key(None, "library_tasks", "work_types", ["work_type_id"], ["id"])


def downgrade():
    op.drop_constraint(None, "library_tasks", type_="foreignkey")
    op.drop_column("library_tasks", "work_type_id")
    op.drop_table("work_type_tenant_link")
    op.drop_table("work_types")
