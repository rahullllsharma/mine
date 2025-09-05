"""Add user to daily report

Revision ID: 25bcb2e5524e
Revises: 280253ca8cbd
Create Date: 2022-02-16 17:56:14.918331

"""
import uuid

import sqlalchemy as sa
import sqlmodel
from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "25bcb2e5524e"
down_revision = "280253ca8cbd"
branch_labels = None
depends_on = None


def upgrade():
    first_user = op.get_bind().execute(text("SELECT id FROM users LIMIT 1")).first()
    first_user_id = None
    if first_user:
        first_user_id = first_user.id
    else:
        first_user_id = uuid.uuid4()
        op.get_bind().execute(
            f"INSERT INTO users (id, keycloak_id, first_name, last_name) VALUES('{first_user_id}'::uuid, '{uuid.uuid4()}'::uuid, 'Undefined', '');"
        )

    op.add_column(
        "daily_reports",
        sa.Column("created_by_id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
    )
    op.execute(f"UPDATE daily_reports SET created_by_id = '{first_user_id}'")
    op.alter_column("daily_reports", "created_by_id", nullable=False)
    op.create_foreign_key(
        "created_by_fk", "daily_reports", "users", ["created_by_id"], ["id"]
    )


def downgrade():
    op.drop_constraint("created_by_fk", "daily_reports", type_="foreignkey")
    op.drop_column("daily_reports", "created_by_id")
