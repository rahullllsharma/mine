"""added seed data for feature flag tables

Revision ID: 75e824f9bdad
Revises: fe6227214387
Create Date: 2023-11-15 20:20:16.648166

"""
import uuid
from typing import Tuple

import sqlalchemy as sa
from alembic import op
from sqlalchemy import text

from migrations.fixtures.feature_flag_seed_data import data as feature_flag_data
from worker_safety_service.urbint_logging import get_logger

logger = get_logger(__name__)
# revision identifiers, used by Alembic.
revision = "75e824f9bdad"
down_revision = "fe6227214387"
branch_labels = None
depends_on = None


def get_existing_feature_flags() -> list[Tuple[str, str]]:
    stmt = "SELECT id, feature_name from feature_flag"
    conn = op.get_bind()
    return conn.execute(text(stmt)).fetchall()


def get_tables():
    meta = sa.MetaData(bind=op.get_bind())

    # """ pass in tuple with tables we want to reflect,
    # otherwise whole database will get reflected"""
    meta.reflect(
        only=(
            "feature_flag",
            "feature_flag_log",
        )
    )

    # define table representation
    feature_flag = sa.Table("feature_flag", meta)
    feature_flag_log = sa.Table("feature_flag_log", meta)
    return feature_flag, feature_flag_log


def upgrade():
    feature_flag, feature_flag_log = get_tables()
    results = get_existing_feature_flags()

    for data in feature_flag_data:
        existing_feature_names = [result[1] for result in results]
        if data["feature_name"] not in existing_feature_names:
            logger.debug(f"adding feature name --> {data['feature_name']}")
            op.execute(feature_flag.insert().values(**data))
            op.execute(
                feature_flag_log.insert().values(
                    id=str(uuid.uuid4()),
                    feature_flag_id=data["id"],
                    configurations=data["configurations"],
                    log_type="CREATE",
                    created_at=data["created_at"],
                )
            )


def downgrade():
    pass
