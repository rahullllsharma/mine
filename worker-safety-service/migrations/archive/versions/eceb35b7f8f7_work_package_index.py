"""Work package index

Revision ID: 97ec238f5a63
Revises: f292e0100502
Create Date: 2022-11-16 10:00:33.277917

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "97ec238f5a63"
down_revision = "f292e0100502"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(
        "projects_tenant_status_idx",
        "projects",
        ["tenant_id", "status"],
        unique=False,
        postgresql_where="archived_at IS NULL",
    )


def downgrade():
    op.drop_index(
        "projects_tenant_status_idx",
        table_name="projects",
        postgresql_where="archived_at IS NULL",
    )
