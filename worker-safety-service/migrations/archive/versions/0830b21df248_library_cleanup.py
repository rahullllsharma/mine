"""Library cleanup

Revision ID: 0830b21df248
Revises: beeac15d6645
Create Date: 2022-06-20 09:56:24.858363

"""

# revision identifiers, used by Alembic.
revision = "0830b21df248"
down_revision = "beeac15d6645"
branch_labels = None
depends_on = None


# Contents removed due to data issue in migration
# see: https://github.com/urbint/worker-safety-service/pull/798
def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
