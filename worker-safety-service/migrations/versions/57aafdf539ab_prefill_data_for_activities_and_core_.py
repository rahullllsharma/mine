"""Prefill data for activities and core work types

Revision ID: 57aafdf539ab
Revises: c38807d82d98
Create Date: 2025-06-16 09:06:45.906168

"""
import logging
import uuid

from alembic import op
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

# revision identifiers, used by Alembic.
revision = "57aafdf539ab"
down_revision = "c38807d82d98"
branch_labels = None
depends_on = None

logger = logging.getLogger(__name__)


def upgrade() -> None:
    # Create a connection
    connection = op.get_bind()

    try:
        # Step 1: Fetch all tenant work types
        tenant_work_types = connection.execute(
            text(
                """
            SELECT id, core_work_type_ids
            FROM work_types
            WHERE tenant_id IS NOT NULL
            AND core_work_type_ids IS NOT NULL
            AND core_work_type_ids != '{}'
        """
            )
        ).fetchall()

        if not tenant_work_types:
            logger.warning("No tenant work types found to process")
            return

        records_created = 0
        # Step 2 & 3: For each tenant work type, process its core work types and their tasks
        for tenant_wt in tenant_work_types:
            tenant_wt_id = tenant_wt[0]
            core_work_type_ids = tenant_wt[1]

            if not core_work_type_ids:
                logger.warning(
                    f"No core work type IDs found for tenant work type {tenant_wt_id}"
                )
                continue

            for core_wt_id in core_work_type_ids:
                # Verify core work type exists
                core_wt_exists = connection.execute(
                    text(
                        """
                    SELECT EXISTS (
                        SELECT 1 FROM work_types WHERE id = :core_wt_id
                    )
                """
                    ),
                    {"core_wt_id": core_wt_id},
                ).scalar()

                if not core_wt_exists:
                    logger.warning(f"Core work type {core_wt_id} not found, skipping")
                    continue

                # Get tasks linked to this core work type
                tasks = connection.execute(
                    text(
                        """
                    SELECT task_id
                    FROM work_type_task_link
                    WHERE work_type_id = :core_wt_id
                """
                    ),
                    {"core_wt_id": core_wt_id},
                ).fetchall()

                if not tasks:
                    logger.warning(f"No tasks found for core work type {core_wt_id}")
                    continue

                # Step 4: Get activity groups for these tasks
                for task in tasks:
                    task_id = task[0]

                    # Verify task exists
                    task_exists = connection.execute(
                        text(
                            """
                        SELECT EXISTS (
                            SELECT 1 FROM library_tasks WHERE id = :task_id
                        )
                    """
                        ),
                        {"task_id": task_id},
                    ).scalar()

                    if not task_exists:
                        logger.warning(f"Library Task {task_id} not found, skipping")
                        continue

                    activity_groups = connection.execute(
                        text(
                            """
                        SELECT activity_group_id
                        FROM library_task_activity_groups
                        WHERE library_task_id = :task_id
                    """
                        ),
                        {"task_id": task_id},
                    ).fetchall()

                    if not activity_groups:
                        logger.warning(
                            f"No activity groups found for library task {task_id}"
                        )
                        continue

                    # Step 5: Create activity work type settings
                    for activity_group in activity_groups:
                        activity_group_id = activity_group[0]

                        # Verify activity group exists
                        activity_group_exists = connection.execute(
                            text(
                                """
                            SELECT EXISTS (
                                SELECT 1 FROM library_activity_groups WHERE id = :activity_group_id
                            )
                        """
                            ),
                            {"activity_group_id": activity_group_id},
                        ).scalar()

                        if not activity_group_exists:
                            logger.warning(
                                f"Activity group {activity_group_id} not found, skipping"
                            )
                            continue

                        # Check if the setting already exists
                        existing_activity_wt_setting = connection.execute(
                            text(
                                """
                            SELECT id
                            FROM activity_worktype_settings
                            WHERE library_activity_group_id = :activity_group_id
                            AND work_type_id = :work_type_id
                        """
                            ),
                            {
                                "activity_group_id": activity_group_id,
                                "work_type_id": tenant_wt_id,
                            },
                        ).fetchone()

                        if not existing_activity_wt_setting:
                            try:
                                # Insert new activity work type setting
                                connection.execute(
                                    text(
                                        """
                                    INSERT INTO activity_worktype_settings
                                    (id, library_activity_group_id, work_type_id, created_at, updated_at)
                                    VALUES
                                    (:id, :library_activity_group_id, :work_type_id, NOW(), NOW())
                                """
                                    ),
                                    {
                                        "id": str(uuid.uuid4()),
                                        "library_activity_group_id": activity_group_id,
                                        "work_type_id": tenant_wt_id,
                                    },
                                )
                                records_created += 1
                            except SQLAlchemyError as e:
                                logger.error(
                                    f"Error creating activity work type setting: {str(e)}"
                                )
                                continue

        logger.info(
            f"Migration completed. Created {records_created} new activity work type settings."
        )

    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        raise


def downgrade() -> None:
    # No downgrade possible for this
    pass
