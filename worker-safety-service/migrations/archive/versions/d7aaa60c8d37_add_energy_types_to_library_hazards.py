"""add energy types to library_hazards

Revision ID: d7aaa60c8d37
Revises: 76e8b1cf2281
Create Date: 2023-05-10 15:01:52.760003

"""
import sqlalchemy as sa
from alembic import op

from worker_safety_service.models.utils import EnumValues

# revision identifiers, used by Alembic.
revision = "d7aaa60c8d37"
down_revision = "5390dc0acd85"
branch_labels = None
depends_on = None

energy_types = [
    "Biological",
    "Chemical",
    "Electrical",
    "Gravity",
    "Mechanical",
    "Motion",
    "Pressure",
    "Radiation",
    "Sound",
    "Temperature",
    "Not Defined",
]

energy_levels = [
    "High Energy",
    "Low Energy",
    "Not Defined",
]


def format(enum_list: list[str]) -> str:
    return ", ".join(map(lambda x: f"'{x}'", enum_list))


def upgrade():
    op.execute(f"CREATE TYPE hazard_energy_types AS ENUM({format(energy_types)})")
    op.execute(f"CREATE TYPE hazard_energy_levels AS ENUM({format(energy_levels)})")
    op.add_column(
        "library_hazards",
        sa.Column(
            "energy_type",
            EnumValues(
                "Biological",
                "Chemical",
                "Electrical",
                "Gravity",
                "Mechanical",
                "Motion",
                "Pressure",
                "Radiation",
                "Sound",
                "Temperature",
                "Not Defined",
                name="hazard_energy_types",
            ),
            nullable=True,
        ),
    )
    op.add_column(
        "library_hazards",
        sa.Column(
            "energy_level",
            EnumValues(
                "high_energy", "low_energy", "Not Defined", name="hazard_energy_levels"
            ),
            nullable=True,
        ),
    )

    op.execute("UPDATE library_hazards SET energy_type = 'Not Defined'")
    op.execute("UPDATE library_hazards SET energy_level = 'Not Defined'")


def downgrade():
    op.drop_column("library_hazards", "energy_level")
    op.drop_column("library_hazards", "energy_type")
    op.execute("drop type hazard_energy_types")
    op.execute("drop type hazard_energy_levels")
