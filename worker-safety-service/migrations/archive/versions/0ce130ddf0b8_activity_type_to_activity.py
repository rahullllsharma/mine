"""Activity type to activity

Revision ID: 0ce130ddf0b8
Revises: 153533218bad
Create Date: 2022-10-14 12:19:57.130606

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "0ce130ddf0b8"
down_revision = "153533218bad"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "activities",
        sa.Column(
            "library_activity_type_id", sqlmodel.sql.sqltypes.GUID(), nullable=True
        ),
    )
    op.create_foreign_key(
        "activities_library_activity_type_id_pkey",
        "activities",
        "library_activity_types",
        ["library_activity_type_id"],
        ["id"],
    )


def downgrade():
    op.drop_constraint(
        "activities_library_activity_type_id_pkey", "activities", type_="foreignkey"
    )
    op.drop_column("activities", "library_activity_type_id")
