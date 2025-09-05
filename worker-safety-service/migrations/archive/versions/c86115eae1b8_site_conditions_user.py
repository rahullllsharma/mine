"""Site conditions user

Revision ID: c86115eae1b8
Revises: 24a8bbe5dbf1
Create Date: 2022-04-22 18:44:10.536645

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "c86115eae1b8"
down_revision = "24a8bbe5dbf1"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "project_location_site_conditions",
        sa.Column("user_id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
    )

    # Update all site condition, we only have manual site conditions
    # Grab user from audit events
    op.execute(
        """
        UPDATE project_location_site_conditions s
        SET user_id = e.user_id
        FROM audit_events e, audit_event_diffs d
        WHERE
            s.id = d.object_id
            AND d.event_id = e.id
            AND e.event_type = 'project_location_site_condition_created'"""
    )
    # If for some reason we didn't add an audit event, just use first user
    users = op.get_bind().execute(text("SELECT id FROM users LIMIT 1")).fetchall()
    if users:
        op.execute(
            f"""
            UPDATE project_location_site_conditions
            SET user_id = '{users[0][0]}'
            WHERE user_id IS NULL"""
        )
    op.create_foreign_key(
        "project_location_site_conditions_user_id_fkey",
        "project_location_site_conditions",
        "users",
        ["user_id"],
        ["id"],
    )


def downgrade():
    op.drop_constraint(
        "project_location_site_conditions_user_id_fkey",
        "project_location_site_conditions",
        type_="foreignkey",
    )
    op.drop_column("project_location_site_conditions", "user_id")
