"""Project division

Revision ID: 00f46e3f7981
Revises: fa1cf0ad941f
Create Date: 2022-01-25 14:44:01.095217

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "00f46e3f7981"
down_revision = "fa1cf0ad941f"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "projects",
        sa.Column("library_division_id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
    )
    library_division_id = (
        op.get_bind().execute("SELECT id FROM library_divisions LIMIT 1").first()[0]
    )
    op.execute(f"UPDATE projects SET library_division_id = '{library_division_id}'")
    op.alter_column("projects", "library_division_id", nullable=False)
    op.create_foreign_key(
        None, "projects", "library_divisions", ["library_division_id"], ["id"]
    )


def downgrade():
    op.drop_constraint(
        "projects_library_division_id_fkey", "projects", type_="foreignkey"
    )
    op.drop_column("projects", "library_division_id")
