"""Migrate hazards and controls recommendations

Revision ID: 057d8e8234d5
Revises: 36edbbeadb1d
Create Date: 2022-01-20 16:05:16.847590

"""
import os

import sqlalchemy as sa
import sqlmodel
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "057d8e8234d5"
down_revision = "36edbbeadb1d"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "library_task_recommendations",
        sa.Column("library_task_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("library_hazard_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("library_control_id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["library_control_id"],
            ["library_controls.id"],
        ),
        sa.ForeignKeyConstraint(
            ["library_hazard_id"],
            ["library_hazards.id"],
        ),
        sa.ForeignKeyConstraint(
            ["library_task_id"],
            ["library_tasks.id"],
        ),
        sa.PrimaryKeyConstraint(
            "library_task_id", "library_hazard_id", "library_control_id"
        ),
    )
    op.drop_table("library_hazard_controls")
    op.drop_table("library_task_hazards")

    directory = os.fsencode("migrations/fixtures/")
    filepath = os.path.join(
        directory, b"postgres_public_library_task_recommendations.sql"
    )
    with open(filepath) as file:
        escaped_sql = sa.text(file.read())
    op.execute(escaped_sql)


def downgrade():
    op.create_table(
        "library_task_hazards",
        sa.Column(
            "library_task_id", postgresql.UUID(), autoincrement=False, nullable=False
        ),
        sa.Column(
            "library_hazard_id", postgresql.UUID(), autoincrement=False, nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["library_hazard_id"],
            ["library_hazards.id"],
            name="library_task_hazards_library_hazard_id_fkey",
        ),
        sa.ForeignKeyConstraint(
            ["library_task_id"],
            ["library_tasks.id"],
            name="library_task_hazards_library_task_id_fkey",
        ),
        sa.PrimaryKeyConstraint(
            "library_task_id", "library_hazard_id", name="library_task_hazards_pkey"
        ),
    )
    op.create_table(
        "library_hazard_controls",
        sa.Column(
            "library_hazard_id", postgresql.UUID(), autoincrement=False, nullable=False
        ),
        sa.Column(
            "library_control_id", postgresql.UUID(), autoincrement=False, nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["library_control_id"],
            ["library_controls.id"],
            name="library_hazard_controls_library_control_id_fkey",
        ),
        sa.ForeignKeyConstraint(
            ["library_hazard_id"],
            ["library_hazards.id"],
            name="library_hazard_controls_library_hazard_id_fkey",
        ),
        sa.PrimaryKeyConstraint(
            "library_hazard_id",
            "library_control_id",
            name="library_hazard_controls_pkey",
        ),
    )
    op.drop_table("library_task_recommendations")

    directory = os.fsencode("migrations/fixtures/")
    included_fixtures = [
        b"postgres_public_library_task_hazards.sql",
        b"postgres_public_library_hazard_controls.sql",
    ]
    for filename in included_fixtures:
        filepath = os.path.join(directory, filename)
        with open(filepath) as file:
            escaped_sql = sa.text(file.read())
        op.execute(escaped_sql)
