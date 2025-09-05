"""supervisor

Revision ID: 417407ce174c
Revises: 224be4eb2c44
Create Date: 2022-01-31 13:58:54.233761

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "417407ce174c"
down_revision = "224be4eb2c44"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "supervisor",
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.execute(
        "ALTER TABLE raw_incidents ALTER COLUMN supervisor_id TYPE uuid USING supervisor_id::uuid"
    )
    op.create_foreign_key(
        "raw_incidents_supervisor_id_fkey",
        "raw_incidents",
        "supervisor",
        ["supervisor_id"],
        ["id"],
    )

    op.execute(
        "ALTER TABLE observation ALTER COLUMN supervisor_id TYPE uuid USING supervisor_id::uuid"
    )
    op.create_foreign_key(
        "observation_supervisor_id_fkey",
        "observation",
        "supervisor",
        ["supervisor_id"],
        ["id"],
    )


def downgrade():
    op.drop_constraint(
        "raw_incidents_supervisor_id_fkey", "raw_incidents", type_="foreignkey"
    )
    op.execute("ALTER TABLE raw_incidents ALTER COLUMN supervisor_id TYPE varchar")

    op.drop_constraint(
        "observation_supervisor_id_fkey", "observation", type_="foreignkey"
    )
    op.execute("ALTER TABLE observation ALTER COLUMN supervisor_id TYPE varchar")

    op.drop_table("supervisor")
