"""Project type

Revision ID: 62e64a294934
Revises: 00f46e3f7981
Create Date: 2022-01-25 14:56:36.926429

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "62e64a294934"
down_revision = "00f46e3f7981"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "projects",
        sa.Column(
            "library_project_type_id", sqlmodel.sql.sqltypes.GUID(), nullable=True
        ),
    )
    library_project_type_id = (
        op.get_bind().execute("SELECT id FROM library_project_types LIMIT 1").first()[0]
    )
    op.execute(
        f"UPDATE projects SET library_project_type_id = '{library_project_type_id}'"
    )
    op.alter_column("projects", "library_project_type_id", nullable=False)
    op.create_foreign_key(
        "projects_library_project_type_id_fkey",
        "projects",
        "library_project_types",
        ["library_project_type_id"],
        ["id"],
    )


def downgrade():
    op.drop_constraint(
        "projects_library_project_type_id_fkey", "projects", type_="foreignkey"
    )
    op.drop_column("projects", "library_project_type_id")
