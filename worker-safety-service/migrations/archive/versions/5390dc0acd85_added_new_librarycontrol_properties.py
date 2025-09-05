"""Added new LibraryControl properties

Revision ID: 5390dc0acd85
Revises: 76e8b1cf2281
Create Date: 2023-05-11 15:09:14.145765

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "5390dc0acd85"
down_revision = "76e8b1cf2281"
branch_labels = None
depends_on = None

e1 = sa.Enum("DIRECT", "INDIRECT", name="type_of_control")
e2 = sa.Enum(
    "ADMINISTRATIVE_CONTROLS",
    "ELIMINATION",
    "ENGINEERING_CONTROLS",
    "PPE",
    "SUBSTITUTION",
    name="osha_controls_classification",
)


def upgrade():
    # Create ENUMS
    e1.create(op.get_bind(), checkfirst=True)
    e2.create(op.get_bind(), checkfirst=True)

    op.add_column("library_controls", sa.Column("type", e1, nullable=True))
    op.add_column(
        "library_controls", sa.Column("osha_classification", e2, nullable=True)
    )
    op.add_column("library_controls", sa.Column("ppe", sa.Boolean(), nullable=True))


def downgrade():
    op.drop_column("library_controls", "ppe")
    op.drop_column("library_controls", "osha_classification")
    op.drop_column("library_controls", "type")

    e2.drop(op.get_bind())
    e1.drop(op.get_bind())
