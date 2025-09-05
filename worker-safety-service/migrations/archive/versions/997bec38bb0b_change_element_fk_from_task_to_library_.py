"""change_element_fk_from_task_to_library_task

Revision ID: 997bec38bb0b
Revises: 006f410e12ef
Create Date: 2022-11-30 10:51:35.374301

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "997bec38bb0b"
down_revision = "006f410e12ef"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "element_library_task_link",
        sa.Column("element_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("library_task_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["element_id"],
            ["elements.id"],
        ),
        sa.ForeignKeyConstraint(
            ["library_task_id"],
            ["library_tasks.id"],
        ),
        sa.PrimaryKeyConstraint("element_id", "library_task_id"),
    )
    op.drop_table("element_task_link")
    op.add_column(
        "compatible_units",
        sa.Column("element_id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
    )
    op.drop_constraint(
        "compatible_units_element_name_fkey", "compatible_units", type_="foreignkey"
    )
    op.create_foreign_key(
        "compatible_units_element_id_fk",
        "compatible_units",
        "elements",
        ["element_id"],
        ["id"],
    )
    op.drop_column("compatible_units", "element_name")


def downgrade():
    op.add_column(
        "compatible_units",
        sa.Column("element_name", sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    op.drop_constraint(
        "compatible_units_element_id_fk", "compatible_units", type_="foreignkey"
    )
    op.create_foreign_key(
        "compatible_units_element_name_fkey",
        "compatible_units",
        "elements",
        ["element_name"],
        ["name"],
    )
    op.drop_column("compatible_units", "element_id")
    op.create_table(
        "element_task_link",
        sa.Column("task_id", postgresql.UUID(), autoincrement=False, nullable=False),
        sa.Column("element_name", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(
            ["element_name"],
            ["elements.name"],
            name="element_task_link_element_name_fkey",
        ),
        sa.ForeignKeyConstraint(
            ["task_id"], ["tasks.id"], name="element_task_link_task_id_fkey"
        ),
    )
    op.drop_table("element_library_task_link")
