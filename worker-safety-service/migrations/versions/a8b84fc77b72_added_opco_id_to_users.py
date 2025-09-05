"""Added opco_id to users

Revision ID: 3d55c64bd96c
Revises: 242a74cd0768
Create Date: 2023-11-14 08:09:34.896934

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "3d55c64bd96c"
down_revision = "242a74cd0768"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "users", sa.Column("opco_id", sqlmodel.sql.sqltypes.GUID(), nullable=True)
    )
    op.create_foreign_key("users_opco_id_fkey", "users", "opcos", ["opco_id"], ["id"])


def downgrade():
    op.drop_constraint("users_opco_id_fkey", "users", type_="foreignkey")
    op.drop_column("users", "opco_id")
