"""create user_preferences table

Revision ID: 141831ac0023
Revises: cf74785f909a
Create Date: 2024-01-26 14:30:45.371632

"""
import enum

import sqlalchemy as sa
import sqlmodel
from alembic import op
from sqlalchemy.dialects import postgresql

from worker_safety_service.models.utils import EnumValues

# revision identifiers, used by Alembic.
revision = "141831ac0023"
down_revision = "cf74785f909a"
branch_labels = None
depends_on = None


@enum.unique
class UserPreferenceEntityType(str, enum.Enum):
    MapFilters = "map_filters"


def upgrade() -> None:
    op.create_table(
        "user_preferences",
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("user_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column(
            "entity_type",
            EnumValues(UserPreferenceEntityType, name="userpreferenceentitytype"),
            nullable=False,
        ),
        sa.Column("contents", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
    )
    op.create_index(
        "user_preferences_user_id_entity_type_ix",
        "user_preferences",
        ["user_id", "entity_type"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "user_preferences_user_id_entity_type_ix", table_name="user_preferences"
    )
    op.execute("DROP TYPE IF EXISTS userpreferenceentitytype CASCADE")
    op.drop_table("user_preferences")
