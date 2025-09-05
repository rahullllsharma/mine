"""Change primary key on parsed files

Revision ID: 89833c24570f
Revises: 0bf15e132c97
Create Date: 2022-04-06 18:11:45.173118

"""
import uuid

import sqlalchemy as sa
import sqlmodel
from alembic import op
from sqlmodel import Session

# revision identifiers, used by Alembic.
revision = "89833c24570f"
down_revision = "0bf15e132c97"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "parsed_files", sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=True)
    )

    with Session(bind=op.get_bind()) as session:
        for parsed_file in session.execute("select * from parsed_files;"):
            update = f"update parsed_files set id='{uuid.uuid4()}' where  file_path='{parsed_file.file_path}';"
            session.execute(update)
            session.commit()

    op.alter_column("parsed_files", "id", nullable=False)

    op.drop_constraint("parsed_files_pkey", "parsed_files")
    op.create_primary_key("parsed_files_id_pkey", "parsed_files", ["id"])


def downgrade():
    op.drop_column("parsed_files", "id")
    op.create_primary_key("parsed_files_pkey", "parsed_files", ["file_path"])
