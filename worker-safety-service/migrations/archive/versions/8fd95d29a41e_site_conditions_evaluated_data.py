"""Site conditions evaluated data

Revision ID: 8fd95d29a41e
Revises: c86115eae1b8
Create Date: 2022-04-27 16:35:55.164263

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "8fd95d29a41e"
down_revision = "c86115eae1b8"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "project_location_site_conditions", sa.Column("date", sa.Date(), nullable=True)
    )
    op.add_column(
        "project_location_site_conditions",
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.add_column(
        "project_location_site_conditions",
        sa.Column("alert", sa.Boolean(), nullable=True),
    )
    op.add_column(
        "project_location_site_conditions",
        sa.Column("multiplier", sa.Float(), nullable=True),
    )
    op.create_index(
        "project_location_site_conditions_evaluated_idx",
        "project_location_site_conditions",
        ["project_location_id", "date"],
        unique=False,
    )
    op.create_unique_constraint(
        "project_location_site_conditions_evaluated_key",
        "project_location_site_conditions",
        ["project_location_id", "library_site_condition_id", "date"],
    )
    op.create_index(
        "project_location_site_conditions_manual_idx",
        "project_location_site_conditions",
        ["project_location_id"],
        unique=False,
        postgresql_where="user_id IS NOT NULL",
    )


def downgrade():
    op.drop_index(
        "project_location_site_conditions_manual_idx",
        table_name="project_location_site_conditions",
        postgresql_where="user_id IS NOT NULL",
    )
    op.drop_constraint(
        "project_location_site_conditions_evaluated_key",
        "project_location_site_conditions",
        type_="unique",
    )
    op.drop_index(
        "project_location_site_conditions_evaluated_idx",
        table_name="project_location_site_conditions",
    )
    op.drop_column("project_location_site_conditions", "multiplier")
    op.drop_column("project_location_site_conditions", "alert")
    op.drop_column("project_location_site_conditions", "details")
    op.drop_column("project_location_site_conditions", "date")
