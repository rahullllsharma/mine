"""Add user id to supervisors

Revision ID: 406dc2dab455
Revises: 62765c0a33d8
Create Date: 2022-02-18 11:31:03.237486

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "406dc2dab455"
down_revision = "c399168483bf"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "supervisor", sa.Column("user_id", sqlmodel.sql.sqltypes.GUID(), nullable=True)
    )
    op.create_foreign_key(
        "supervisors_user_id_fkey", "supervisor", "users", ["user_id"], ["id"]
    )


def downgrade():
    op.drop_constraint("supervisors_user_id_fkey", "supervisor", type_="foreignkey")
    op.drop_column("supervisor", "user_id")
