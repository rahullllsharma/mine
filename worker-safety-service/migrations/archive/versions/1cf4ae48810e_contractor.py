"""Contractor

Revision ID: 1cf4ae48810e
Revises: 3cf5963680b3
Create Date: 2022-01-27 15:46:45.718819

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "1cf4ae48810e"
down_revision = "45b98093cb11"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TABLE raw_incidents ALTER COLUMN incident_id TYPE varchar")

    op.create_table(
        "contractor",
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.add_column(
        "observation",
        sa.Column(
            "contractor_involved_id", sqlmodel.sql.sqltypes.GUID(), nullable=True
        ),
    )
    op.alter_column("observation", "id", existing_type=sa.VARCHAR(), nullable=True)
    op.alter_column(
        "observation", "project_id", existing_type=sa.VARCHAR(), nullable=True
    )
    op.create_foreign_key(
        "observation_contractor_involved_id_fkey",
        "observation",
        "contractor",
        ["contractor_involved_id"],
        ["id"],
    )
    op.drop_column("observation", "contractor_involved")
    op.add_column(
        "raw_incidents",
        sa.Column("contractor_id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
    )
    op.alter_column(
        "raw_incidents", "project_id", existing_type=sa.VARCHAR(), nullable=True
    )
    op.create_foreign_key(
        "raw_incidents_contractor_id_fkey",
        "raw_incidents",
        "contractor",
        ["contractor_id"],
        ["id"],
    )
    op.drop_column("raw_incidents", "contractor")


def downgrade():
    op.execute(
        """
        ALTER TABLE raw_incidents
        ALTER COLUMN incident_id
        TYPE uuid
        USING uuid_in(md5(random()::text || clock_timestamp()::text)::cstring)
        """
    )

    op.add_column(
        "raw_incidents",
        sa.Column("contractor", sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    op.drop_constraint(
        "raw_incidents_contractor_id_fkey", "raw_incidents", type_="foreignkey"
    )
    op.alter_column(
        "raw_incidents", "project_id", existing_type=sa.VARCHAR(), nullable=False
    )
    op.drop_column("raw_incidents", "contractor_id")
    op.add_column(
        "observation",
        sa.Column(
            "contractor_involved", sa.VARCHAR(), autoincrement=False, nullable=True
        ),
    )
    op.drop_constraint(
        "observation_contractor_involved_id_fkey", "observation", type_="foreignkey"
    )
    op.alter_column(
        "observation", "project_id", existing_type=sa.VARCHAR(), nullable=False
    )
    op.alter_column("observation", "id", existing_type=sa.VARCHAR(), nullable=False)
    op.drop_column("observation", "contractor_involved_id")
    op.drop_table("contractor")
