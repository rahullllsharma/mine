"""Fixing incorrect contractor name

Revision ID: d2796d51fa70
Revises: 0830b21df248
Create Date: 2022-06-30 14:07:36.375917

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "d2796d51fa70"
down_revision = "031ae058c69f"
branch_labels = None
depends_on = None


def upgrade():
    # rename records where name = 'Mullen & Sons' to 'J Mullen & Sons'
    # if no existing contractor with new name
    # and exactly one contractor with old name
    new = "J Mullen & Sons"
    old = "Mullen & Sons"
    op.execute(
        f"""
        UPDATE contractor
        SET name = '{new}'
        WHERE name = '{old}'
        AND NOT EXISTS (select name from contractor where name='{new}')
        AND EXISTS (with ensure_one as (select count(*) over (partition by name) as count from contractor where name = '{old}')
                    select * from ensure_one where count = 1);
    """
    )
    op.execute(
        f"""
        UPDATE contractor_aliases
        SET alias = '{new}'
        WHERE alias = '{old}'
        AND NOT EXISTS (select alias from contractor_aliases where alias='{new}')
        AND EXISTS (with ensure_one as (select count(*) over (partition by alias) as count from contractor_aliases where alias = '{old}')
                    select * from ensure_one where count = 1);
    """
    )


def downgrade():
    # reverse new & old from upgrade
    new = "Mullen & Sons"
    old = "J Mullen & Sons"
    op.execute(
        f"""
        UPDATE contractor
        SET name = '{new}'
        WHERE name = '{old}'
        AND NOT EXISTS (select name from contractor where name='{new}')
        AND EXISTS (with ensure_one as (select count(*) over (partition by name) as count from contractor where name = '{old}')
                    select * from ensure_one where count = 1);
    """
    )
    op.execute(
        f"""
        UPDATE contractor_aliases
        SET alias = '{new}'
        WHERE alias = '{old}'
        AND NOT EXISTS (select alias from contractor_aliases where alias='{new}')
        AND EXISTS (with ensure_one as (select count(*) over (partition by alias) as count from contractor_aliases where alias = '{old}')
                    select * from ensure_one where count = 1);
    """
    )
