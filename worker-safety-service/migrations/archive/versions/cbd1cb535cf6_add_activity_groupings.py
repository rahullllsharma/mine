"""Add activity groupings

Revision ID: cbd1cb535cf6
Revises: 99f5dd0f5eab
Create Date: 2022-09-27 13:36:14.119947

"""

import sqlalchemy as sa
import sqlmodel
from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "cbd1cb535cf6"
down_revision = "99f5dd0f5eab"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "activity_groups",
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column(
            "activity_group_name", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("activity_group_name"),
    )

    op.create_table(
        "library_task_activity_groups",
        sa.Column(
            "activity_group_id",
            sqlmodel.sql.sqltypes.GUID(),
            nullable=False,
            primary_key=True,
        ),
        sa.Column(
            "library_task_id",
            sqlmodel.sql.sqltypes.GUID(),
            nullable=False,
            primary_key=True,
        ),
        sa.ForeignKeyConstraint(
            ["activity_group_id"],
            ["activity_groups.id"],
        ),
        sa.ForeignKeyConstraint(
            ["library_task_id"],
            ["library_tasks.id"],
        ),
    )

    activity_groups = [
        {
            "id": "8cfa3513-a393-4834-98e7-f2f279fc8ac1",
            "activity_group_name": "Above-ground Welding",
        },
        {
            "id": "10821d15-975a-4698-8c9d-b4a1936609dd",
            "activity_group_name": "In-trench Welding",
        },
        {
            "id": "13e0a520-8de1-4579-9d77-c76c54982828",
            "activity_group_name": "Confined Space Entry",
        },
        {
            "id": "6693defe-d58d-4f5a-a7da-b269d4a581d9",
            "activity_group_name": "Demolition",
        },
        {
            "id": "ba227d34-44bc-4384-8da8-3d58cc4fc075",
            "activity_group_name": "Drilling",
        },
        {
            "id": "a0da67f3-8c07-46b1-a527-3eb761c61f5f",
            "activity_group_name": "Driving",
        },
        {
            "id": "3d62c233-1c09-499c-a7ac-bb4f895cda04",
            "activity_group_name": "Electrical",
        },
        {
            "id": "524bcf3a-1ddb-4b2d-91e6-97013241689b",
            "activity_group_name": "Excavation",
        },
        {
            "id": "3a522493-0a25-4719-b7ce-8d87b91c7452",
            "activity_group_name": "Field coating - Install/Remove",
        },
        {
            "id": "1e4c6c0a-c675-4be0-a451-2692467fd25a",
            "activity_group_name": "Install Equipment",
        },
        {
            "id": "66958300-e5ee-4809-b6bc-34d74338eab3",
            "activity_group_name": "Labor",
        },
        {
            "id": "a53c4860-62f2-40b9-89cb-4e89c0480a29",
            "activity_group_name": "Material Bending",
        },
        {
            "id": "314350b9-79e3-43ea-8167-4ede2a4eca4a",
            "activity_group_name": "Material Handling",
        },
        {
            "id": "7ce5d4ec-e20d-4703-bedd-eb1ae870a580",
            "activity_group_name": "Non-destructive Examination",
        },
        {
            "id": "313e6685-b8c0-460e-b384-9ef415311a03",
            "activity_group_name": "Other Field Work",
        },
        {
            "id": "d5f625a0-ea44-4dc9-990c-e94b25877ff1",
            "activity_group_name": "Pigging",
        },
        {
            "id": "c3d0d6ee-33f2-43bd-8acf-b8486a78c94c",
            "activity_group_name": "Retire/Remove",
        },
        {
            "id": "cc13a4a3-00fa-43af-9709-bf5767d99a24",
            "activity_group_name": "Pipe Fusion",
        },
        {
            "id": "989a3cae-4be2-4ac6-aa3b-a5ebbd459f79",
            "activity_group_name": "Pipe Installation",
        },
        {
            "id": "4d4b0fd2-7a93-4478-874a-db5b542a0f36",
            "activity_group_name": "Plumbing",
        },
        {
            "id": "44965da2-5d7c-412f-97ee-c6b4c0ade8ff",
            "activity_group_name": "Pressure Test",
        },
        {
            "id": "1255dac3-e7b2-421c-b532-dfb53268e09b",
            "activity_group_name": "Purging",
        },
        {
            "id": "22172a0d-dfcb-46b6-b543-3593d5084873",
            "activity_group_name": "Purging/Gas-in",
        },
        {
            "id": "263b01e7-f705-44a2-a8c1-82290b713ec8",
            "activity_group_name": "Site Setup/Mobilization",
        },
        {
            "id": "2c227a95-c883-4758-8350-92c5528ee6cf",
            "activity_group_name": "Site Prep/Restoration",
        },
        {
            "id": "b5d41b25-58c6-4b0d-9f31-1d3df4ce5ce4",
            "activity_group_name": "Site Restoration",
        },
        {
            "id": "eedcdbc9-f25f-45f1-b2c3-87e7aa5b80f1",
            "activity_group_name": "Tie-in",
        },
        {
            "id": "c0d44bd5-d17c-4d45-9452-dc195e432e71",
            "activity_group_name": "Torquing/Bolt up",
        },
        {
            "id": "0416f434-43d5-45c8-a032-e10dc53a96e7",
            "activity_group_name": "Corrosion",
        },
    ]

    insert_query = """
    INSERT INTO public.activity_groups(id, activity_group_name) VALUES (:id, :activity_group_name);
    """

    conn = op.get_bind()
    for group in activity_groups:
        conn.execute(text(insert_query), group)


def downgrade():
    op.drop_table("library_task_activity_groups")
    op.drop_table("activity_groups")
