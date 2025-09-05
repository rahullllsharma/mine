"""Add additional activity groups

Revision ID: f6d155da117d
Revises: 3db47f006a93
Create Date: 2022-10-10 11:04:21.251796

"""
from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "f6d155da117d"
down_revision = "3db47f006a93"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute(
        text(
            """INSERT INTO activity_groups(id, activity_group_name) values ('1f8e5b52-31dc-45e7-8b50-cdf0fd0a3223', 'Clearance')"""
        )
    )
    conn.execute(
        text(
            """INSERT INTO activity_groups(id, activity_group_name) values ('00ef4058-ad6e-4781-ae1e-4fcd72839e32', 'Phasing')"""
        )
    )
    conn.execute(
        text(
            """INSERT INTO activity_groups(id, activity_group_name) values ('b37ff0fd-9c8e-474b-a412-39dcdc357a89', 'Site Prep')"""
        )
    )
    conn.execute(
        text(
            """INSERT INTO activity_groups(id, activity_group_name) values ('6c26e14a-43ca-4657-af27-65df8d630e59', 'Switching')"""
        )
    )
    conn.execute(
        text(
            """INSERT INTO activity_groups(id, activity_group_name) values ('6cd56ae8-b45f-4ebc-9e7f-5a0e4e705472', 'Work Method')"""
        )
    )


def downgrade():
    pass
