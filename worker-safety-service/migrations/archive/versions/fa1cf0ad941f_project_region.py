"""Project region

Revision ID: fa1cf0ad941f
Revises: dd6bcd96679f
Create Date: 2022-01-25 12:38:17.381162

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "fa1cf0ad941f"
down_revision = "dd6bcd96679f"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "projects",
        sa.Column("library_region_id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
    )
    library_region_id = (
        op.get_bind().execute("SELECT id FROM library_regions LIMIT 1").first()[0]
    )
    op.execute(f"UPDATE projects SET library_region_id = '{library_region_id}'")
    op.alter_column("projects", "library_region_id", nullable=False)
    op.create_foreign_key(
        None, "projects", "library_regions", ["library_region_id"], ["id"]
    )


def downgrade():
    op.drop_constraint(
        "projects_library_region_id_fkey", "projects", type_="foreignkey"
    )
    op.drop_column("projects", "library_region_id")
