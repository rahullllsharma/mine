"""Migrated calculated site conditions

Revision ID: 1b4b3893b602
Revises: 0fb6e9e76950
Create Date: 2022-04-27 18:47:31.432243

"""
import uuid
from collections import defaultdict

import sqlalchemy as sa
from alembic import op
from sqlalchemy import MetaData, Table, text
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "1b4b3893b602"
down_revision = "0fb6e9e76950"
branch_labels = None
depends_on = None


def upgrade():
    # Migrate from calculated to site condition table and add hazards/controls recommendations
    calculated = list(
        op.get_bind().execute(
            text(
                """
        SELECT id, project_location_id, library_site_condition_id, date, details, alert, multiplier
        FROM (
            SELECT
                DISTINCT ON (project_location_id, library_site_condition_id, date)
                *
            FROM calculated_project_location_site_condition
            ORDER BY project_location_id, library_site_condition_id, date, calculated_at DESC
        ) x
        """
            )
        )
    )

    if calculated:
        recommendations = get_recommendations(calculated)
        all_hazards_manually_added, all_controls_manually_added = get_manually_added(
            calculated
        )

        # Add hazards/controls recommendations and manually added to calculated site conditions
        site_condition_to_add = []
        hazard_to_add = []
        control_to_add = []
        for calculated_site_condition in calculated:
            # Add evaluated site conditions
            site_condition_to_add.append(
                {
                    "id": str(calculated_site_condition.id),
                    "project_location_id": str(
                        calculated_site_condition.project_location_id
                    ),
                    "library_site_condition_id": str(
                        calculated_site_condition.library_site_condition_id
                    ),
                    "date": calculated_site_condition.date,
                    "details": calculated_site_condition.details,
                    "alert": calculated_site_condition.alert,
                    "multiplier": calculated_site_condition.multiplier,
                }
            )

            # Add hazards, we need to check library recommendations and manually added
            hazard_position = 0
            hazards_manually_added = all_hazards_manually_added.pop(
                (
                    calculated_site_condition.project_location_id,
                    calculated_site_condition.library_site_condition_id,
                ),
                {},
            )
            for library_hazard_id, hazard_controls in recommendations[
                calculated_site_condition.library_site_condition_id
            ].items():
                # If we have a hazard recommendation, we can ignore the manually added
                hazards_manually_added.pop(library_hazard_id, None)

                hazard_id = uuid.uuid4()
                hazard_to_add.append(
                    {
                        "id": str(hazard_id),
                        "project_location_site_condition_id": str(
                            calculated_site_condition.id
                        ),
                        "library_hazard_id": str(library_hazard_id),
                        "is_applicable": True,
                        "position": hazard_position,
                    }
                )
                hazard_position += 1

                # Add controls, we need to check library recommendations and manually added
                control_position = 0
                controls_manually_added = all_controls_manually_added.pop(
                    (
                        calculated_site_condition.project_location_id,
                        calculated_site_condition.library_site_condition_id,
                        library_hazard_id,
                    ),
                    {},
                )
                for library_control_id in hazard_controls:
                    # If we have a control recommendation, we can ignore the manually added
                    controls_manually_added.pop(library_control_id, None)

                    control_to_add.append(
                        {
                            "id": str(uuid.uuid4()),
                            "project_location_site_condition_hazard_id": str(hazard_id),
                            "library_control_id": str(library_control_id),
                            "is_applicable": True,
                            "position": control_position,
                        }
                    )
                    control_position += 1

                # Add manually added controls, if not added by recommendation
                for library_control_id, (
                    control_is_applicable,
                    control_user_id,
                ) in controls_manually_added.items():
                    control_to_add.append(
                        {
                            "id": uuid.uuid4(),
                            "project_location_site_condition_hazard_id": str(hazard_id),
                            "library_control_id": str(library_control_id),
                            "is_applicable": control_is_applicable,
                            "user_id": str(control_user_id)
                            if control_user_id
                            else None,
                            "position": control_position,
                        }
                    )
                    control_position += 1

            # Add manually added hazards, if not added by recommendation
            for library_hazard_id, (
                hazard_is_applicable,
                hazard_user_id,
            ) in hazards_manually_added.items():
                hazard_id = uuid.uuid4()
                hazard_to_add.append(
                    {
                        "id": str(hazard_id),
                        "project_location_site_condition_id": str(
                            calculated_site_condition.id
                        ),
                        "library_hazard_id": str(library_hazard_id),
                        "is_applicable": hazard_is_applicable,
                        "user_id": str(hazard_user_id) if hazard_user_id else None,
                        "position": hazard_position,
                    }
                )
                hazard_position += 1

                # Add manually added controls
                control_position = 0
                for library_control_id, (
                    control_is_applicable,
                    control_user_id,
                ) in all_controls_manually_added.pop(
                    (
                        calculated_site_condition.project_location_id,
                        calculated_site_condition.library_site_condition_id,
                        library_hazard_id,
                    ),
                    {},
                ).items():
                    control_to_add.append(
                        {
                            "id": uuid.uuid4(),
                            "project_location_site_condition_hazard_id": str(hazard_id),
                            "library_control_id": str(library_control_id),
                            "is_applicable": control_is_applicable,
                            "user_id": str(control_user_id)
                            if control_user_id
                            else None,
                            "position": control_position,
                        }
                    )
                    control_position += 1

        meta = MetaData(bind=op.get_bind())
        meta.reflect(
            only=(
                "project_location_site_conditions",
                "project_location_site_condition_hazards",
                "project_location_site_condition_hazard_controls",
            )
        )
        op.bulk_insert(
            Table("project_location_site_conditions", meta), site_condition_to_add
        )
        op.bulk_insert(
            Table("project_location_site_condition_hazards", meta), hazard_to_add
        )
        op.bulk_insert(
            Table("project_location_site_condition_hazard_controls", meta),
            control_to_add,
        )

    op.drop_table("calculated_project_location_site_condition")


def downgrade():
    op.create_table(
        "calculated_project_location_site_condition",
        sa.Column("date", sa.DATE(), autoincrement=False, nullable=True),
        sa.Column(
            "calculated_at",
            postgresql.TIMESTAMP(timezone=True),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column("id", postgresql.UUID(), autoincrement=False, nullable=False),
        sa.Column(
            "project_location_id",
            postgresql.UUID(),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "library_site_condition_id",
            postgresql.UUID(),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column("alert", sa.BOOLEAN(), autoincrement=False, nullable=False),
        sa.Column(
            "details",
            postgresql.JSONB(astext_type=sa.Text()),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "multiplier",
            postgresql.DOUBLE_PRECISION(precision=53),
            server_default=sa.text("'0'::double precision"),
            autoincrement=False,
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["library_site_condition_id"],
            ["library_site_conditions.id"],
            name="calculated_project_location_site_library_site_condition_id_fkey",
        ),
        sa.ForeignKeyConstraint(
            ["project_location_id"],
            ["project_locations.id"],
            name="calculated_project_location_site_condi_project_location_id_fkey",
        ),
        sa.PrimaryKeyConstraint(
            "id", name="calculated_project_location_site_condition_pkey"
        ),
    )

    # Migrate from site condition table to calculated
    op.execute(
        """
        INSERT INTO calculated_project_location_site_condition
            (id, project_location_id, library_site_condition_id, date, details, alert, multiplier, calculated_at)
            SELECT id, project_location_id, library_site_condition_id, date, details, alert, multiplier, NOW()
            FROM project_location_site_conditions
            WHERE user_id IS NULL"""
    )
    op.execute("DELETE FROM project_location_site_conditions WHERE user_id IS NULL")


def get_recommendations(
    calculated,
) -> defaultdict[uuid.UUID, defaultdict[uuid.UUID, list[uuid.UUID]]]:
    ids = {i.library_site_condition_id for i in calculated}
    # Get recommendations and manually added
    ids_for_query = "'" + "','".join(map(str, ids)) + "'"
    recommendations = defaultdict(lambda: defaultdict(list))
    for item in op.get_bind().execute(
        f"""
        SELECT library_site_condition_id, library_hazard_id, library_control_id
        FROM library_site_condition_recommendations
        WHERE library_site_condition_id IN ({ids_for_query})
        """
    ):
        recommendations[item.library_site_condition_id][item.library_hazard_id].append(
            item.library_control_id
        )
    return recommendations


def get_manually_added(
    calculated,
) -> tuple[
    defaultdict[tuple[uuid.UUID, uuid.UUID], dict[uuid.UUID, tuple[bool, uuid.UUID]]],
    defaultdict[
        tuple[uuid.UUID, uuid.UUID, uuid.UUID], dict[uuid.UUID, tuple[bool, uuid.UUID]]
    ],
]:
    ids = {i.project_location_id for i in calculated}
    ids_for_query = "'" + "','".join(map(str, ids)) + "'"
    hazards = defaultdict(dict)
    controls = defaultdict(dict)
    for item in op.get_bind().execute(
        f"""
        SELECT
            s.project_location_id,
            s.library_site_condition_id,
            h.library_hazard_id,
            h.is_applicable hazard_is_applicable,
            h.user_id hazard_user_id,
            c.library_control_id,
            c.is_applicable control_is_applicable,
            c.user_id control_user_id
        FROM
            project_location_site_conditions s,
            project_location_site_condition_hazards h
                LEFT JOIN project_location_site_condition_hazard_controls c ON (h.id = c.project_location_site_condition_hazard_id)
        WHERE s.id = h.project_location_site_condition_id AND s.library_site_condition_id IN ({ids_for_query})
        """
    ):
        h_key = (item.project_location_id, item.library_site_condition_id)
        hazards[h_key][item.library_hazard_id] = (
            item.hazard_is_applicable,
            item.hazard_user_id,
        )
        if item.library_control_id:
            c_key = (
                item.project_location_id,
                item.library_site_condition_id,
                item.library_hazard_id,
            )
            controls[c_key][item.library_control_id] = item

    return hazards, controls
