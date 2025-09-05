"""Update existing HighEnergyTaskConcept objects

Revision ID: d8ab0fc7aee1
Revises: d99abcb1435c
Create Date: 2023-11-29 12:15:55.874673

"""
import json
import uuid

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "d8ab0fc7aee1"
down_revision = "d99abcb1435c"
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()

    ebo_query = """
    SELECT id, contents, tenant_id
    FROM public.energy_based_observations
    WHERE
        contents IS NOT NULL
        AND contents->>'high_energy_tasks' IS NOT NULL;
    """

    activity_groups_for_tenant_query = """
    SELECT lag.id AS activity_group_id, lag.name AS activity_group_name, ltag.library_task_id AS library_task_id
    FROM library_activity_groups lag
        INNER JOIN library_task_activity_groups ltag ON lag.id = ltag.activity_group_id
        INNER JOIN work_type_task_link wttl ON ltag.library_task_id = wttl.task_id
        INNER JOIN work_type_tenant_link ON wttl.work_type_id = work_type_tenant_link.work_type_id
    WHERE work_type_tenant_link.tenant_id = :tenant_id
    ORDER BY library_task_id;
    """

    # dict with key of tenant id and value of activity groups for that tenant
    tenant_activity_groups_map: dict[
        uuid.UUID, dict[uuid.UUID, list[tuple[uuid.UUID, str]]]
    ] = {}

    sql = sa.text(ebo_query)
    ebos = connection.execute(sql)

    for ebo in ebos:
        tenant_id = ebo.tenant_id

        # Activity groups will vary by tenant as each tenant can have different
        # work types linked. This section builds a data structure to store these
        # in memory so the query is called only once per tenant.
        if tenant_id not in tenant_activity_groups_map:
            sql = sa.text(activity_groups_for_tenant_query)
            activity_groups_rows = connection.execute(sql, {"tenant_id": tenant_id})

            # Here we build a data structure for storing the activity groups by
            # library task id. We do this to make the extracting of data simpler
            # later on.

            # dict with key of library task id and value of activity groups for that library task
            # activity groups are a tuple of (activity_group_id, activity_group_name)
            library_task_to_activity_group_map: dict[
                uuid.UUID, list[tuple[uuid.UUID, str]]
            ] = {}

            for row in activity_groups_rows:
                library_task_id = row.library_task_id
                if library_task_id not in library_task_to_activity_group_map:
                    library_task_to_activity_group_map[library_task_id] = []

                library_task_to_activity_group_map[library_task_id].append(
                    (row.activity_group_id, row.activity_group_name)
                )

            tenant_activity_groups_map[tenant_id] = library_task_to_activity_group_map

        # dict with key of library task id and value of activity groups for that library task
        activity_groups_by_library_task_id = tenant_activity_groups_map[tenant_id]

        # Get the high energy tasks section of contents
        contents: dict = ebo.contents
        high_energy_tasks: list[dict] = contents.get("high_energy_tasks", [])

        # If there are no high energy tasks, skip this ebo
        if len(high_energy_tasks) == 0:
            continue

        # iterate over the high energy tasks
        for high_energy_task in high_energy_tasks:
            # Get the library task id from the high energy task and cast it to a
            # UUID so it can be used as a key to the dict
            library_task_id_str: str = high_energy_task["id"]
            library_task_id: uuid.UUID = uuid.UUID(library_task_id_str)

            # Here we just get the first activity group we find for the library
            # task id. This isn't technically correct as a library task can
            # exist in multiple activity groups. However, the way around this
            # would be to iterate over the `activities` section of `contents`
            # and try to match on the activity name, which also isn't perfect.
            # This should be fine, though, as when this migration gets run it
            # will be on EBOs before the feature is fully live for any tenant.
            try:
                (
                    activity_group_id,
                    activity_group_name,
                ) = activity_groups_by_library_task_id[library_task_id][0]

                # Add the activity group id and name to the high energy task
                high_energy_task["activity_id"] = str(activity_group_id)
                high_energy_task["activity_name"] = activity_group_name
            except KeyError:
                print(
                    f"library_task_id {library_task_id} is not in any activity groups"
                )
                # If there is no activity group for the library task id set the
                # values to None (null in the database)
                high_energy_task["activity_id"] = None
                high_energy_task["activity_name"] = None

        # Convert the contents back to json
        new_contents_json = json.dumps(contents)

        # Update the row with the modified JSON data
        connection.execute(
            sa.text(
                "UPDATE public.energy_based_observations SET contents = :new_contents WHERE id = :id"
            ),
            {"new_contents": new_contents_json, "id": ebo.id},
        )

    pass


def downgrade():
    connection = op.get_bind()

    ebo_query = """
    SELECT id, contents, tenant_id
    FROM public.energy_based_observations
    WHERE
        contents IS NOT NULL
        AND contents->>'high_energy_tasks' IS NOT NULL;
    """

    sql = sa.text(ebo_query)
    ebos = connection.execute(sql)

    for ebo in ebos:
        old_contents: dict = ebo.contents
        # get the high energy tasks section of contents
        high_energy_tasks: list[dict] = old_contents.get("high_energy_tasks", [])

        # if there are no high energy tasks, skip this ebo
        if len(high_energy_tasks) == 0:
            continue

        # iterate over the high energy tasks
        for high_energy_task in high_energy_tasks:
            # remove the activity group id and name from the high energy task
            if "activity_id" in high_energy_task:
                del high_energy_task["activity_id"]
            if "activity_name" in high_energy_task:
                del high_energy_task["activity_name"]

        # convert the contents back to json
        new_contents_json = json.dumps(old_contents)

        # Update the row with the modified JSON data
        connection.execute(
            sa.text(
                "UPDATE public.energy_based_observations SET contents = :new_contents WHERE id = :id"
            ),
            {"new_contents": new_contents_json, "id": ebo.id},
        )
        pass
    pass
