"""Rerun (Hotfix Release 1.27.2): New Signed URLs for ebos with photo attachments

Revision ID: 42080eb6bb1d
Revises: b83653244c79
Create Date: 2025-06-20 14:41:55.559965

"""

from datetime import timedelta

import sqlalchemy as sa
from alembic import op
from sqlalchemy.orm import Session, sessionmaker

from worker_safety_service.gcloud.storage import FileStorage
from worker_safety_service.models.concepts import EnergyBasedObservationLayout

# revision identifiers, used by Alembic.
revision = "42080eb6bb1d"
down_revision = "b83653244c79"
branch_labels = None
depends_on = None

EXPIRATION_DAYS = 365


def update_photo_signed_urls(file_storage: FileStorage, contents: dict) -> str:
    ebo_layout = EnergyBasedObservationLayout.parse_obj(contents)
    if ebo_layout.photos:
        for file in ebo_layout.photos:
            if file.id:
                _url = file_storage._url(
                    file.id, expiration=timedelta(days=EXPIRATION_DAYS)
                )
                if not _url.endswith("""/%s"""):
                    file.signed_url = _url
    return ebo_layout.json()


def update_existing_ebo_contents(
    file_storage: FileStorage, session: Session, ebos: list
) -> None:
    for ebo_id, contents in ebos:
        updated_contents = update_photo_signed_urls(file_storage, contents)
        update_query = sa.text(
            """
            UPDATE public.energy_based_observations
            SET contents = :contents
            WHERE id = :id;
        """
        )
        session.execute(update_query, {"id": ebo_id, "contents": updated_contents})

    session.commit()


def upgrade() -> None:
    connection = op.get_bind()
    db_session = sessionmaker(bind=connection)
    file_storage = FileStorage()
    session = db_session()

    query_ebos_with_photo_attachments = """
    SELECT id, contents
    FROM energy_based_observations ebo
    WHERE ebo.archived_at IS NULL AND ebo.contents->>'photos' IS NOT NULL AND jsonb_array_length(contents->'photos') > 0;
    """
    _sql = sa.text(query_ebos_with_photo_attachments)
    ebos = connection.execute(_sql).fetchall()

    update_existing_ebo_contents(file_storage=file_storage, session=session, ebos=ebos)


def downgrade() -> None:
    ...
