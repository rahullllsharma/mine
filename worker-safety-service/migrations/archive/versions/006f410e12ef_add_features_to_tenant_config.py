"""Add "FEATURES.IS_ARCHIVE_ALL_ENABLED" defult value

Revision ID: 006f410e12ef
Revises: af6ade335f11
Create Date: 2022-11-22 11:19:29.122192

"""
import uuid

from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "006f410e12ef"
down_revision = "bd772bbd83ed"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()

    count_query = text(
        "SELECT COUNT(*) FROM public.configurations WHERE name = :name and tenant_id is NULL;"
    )
    insert_query = text(
        "INSERT INTO public.configurations (id, name, value) VALUES (:id, :name, :value)"
    )

    params = {
        "id": uuid.uuid4(),
        "name": "FEATURES.IS_ARCHIVE_ALL_WORK_PACKAGES_ENABLED",
        "value": "false",
    }
    n_records_found = conn.scalar(count_query, params)
    if n_records_found == 0:
        conn.execute(insert_query, params)


def downgrade():
    pass
