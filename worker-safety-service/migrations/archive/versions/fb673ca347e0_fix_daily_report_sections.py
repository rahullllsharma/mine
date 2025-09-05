"""Fix daily report sections

Revision ID: fb673ca347e0
Revises: 48de052bea90
Create Date: 2022-02-28 23:58:00.207813

"""
import json

from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "fb673ca347e0"
down_revision = "48de052bea90"
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    for entry in connection.execute(
        "SELECT id, sections FROM daily_reports WHERE sections IS NOT NULL"
    ).all():
        if isinstance(entry.sections, str):
            connection.execute(
                text("UPDATE daily_reports SET sections = :sections WHERE id = :id"),
                sections=entry.sections,
                id=entry.id,
            )


def downgrade():
    connection = op.get_bind()
    for entry in connection.execute(
        "SELECT id, sections FROM daily_reports WHERE sections IS NOT NULL"
    ).all():
        if not isinstance(entry.sections, str):
            connection.execute(
                text("UPDATE daily_reports SET sections = :sections WHERE id = :id"),
                sections=json.dumps(json.dumps(entry.sections)),
                id=entry.id,
            )
