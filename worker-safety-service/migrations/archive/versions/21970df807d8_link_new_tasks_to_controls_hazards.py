"""Link new tasks to controls, hazards

Revision ID: 21970df807d8
Revises: 804759a3e203
Create Date: 2022-10-10 15:35:54.572629

"""
from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "21970df807d8"
down_revision = "804759a3e203"
branch_labels = None
depends_on = None


data = [
    (
        "07a3c9b1-b4aa-4b67-a6ff-dbd3603c1b51",
        "1a5bfa7b-999f-42ca-b3a3-3ab238c8abd6",
        "85abffe4-0558-462b-b17f-65d8f6ecb910",
    ),
    (
        "860ed6da-9864-44e5-b6bf-f06192638566",
        "0db44d38-fa65-4aa5-99bd-ab4a7ec0c880",
        "e92f3626-be91-47da-b197-77e6154f5a15",
    ),
    (
        "860ed6da-9864-44e5-b6bf-f06192638566",
        "0db44d38-fa65-4aa5-99bd-ab4a7ec0c880",
        "52182601-b5ef-4526-ad02-5d63f5b75e84",
    ),
    (
        "860ed6da-9864-44e5-b6bf-f06192638566",
        "1a5bfa7b-999f-42ca-b3a3-3ab238c8abd6",
        "62ca2539-c0c4-4920-aca8-60e8536e725d",
    ),
    (
        "860ed6da-9864-44e5-b6bf-f06192638566",
        "1a5bfa7b-999f-42ca-b3a3-3ab238c8abd6",
        "845518bd-2a56-47c7-92d7-220087939243",
    ),
    (
        "860ed6da-9864-44e5-b6bf-f06192638566",
        "1a5bfa7b-999f-42ca-b3a3-3ab238c8abd6",
        "4ae1251c-d1ea-4ed1-b0b5-9a27b800ff3e",
    ),
    (
        "860ed6da-9864-44e5-b6bf-f06192638566",
        "23041379-366e-4ab2-a0db-a18b569bdafb",
        "9e21d7c7-3276-406e-951e-a710c5c3f35a",
    ),
    (
        "860ed6da-9864-44e5-b6bf-f06192638566",
        "23041379-366e-4ab2-a0db-a18b569bdafb",
        "ddb617a0-9e06-4599-9b99-3e36e7b5ee28",
    ),
    (
        "860ed6da-9864-44e5-b6bf-f06192638566",
        "23041379-366e-4ab2-a0db-a18b569bdafb",
        "a1331fdc-0331-4ef0-984a-3acaa5c3b8e7",
    ),
    (
        "860ed6da-9864-44e5-b6bf-f06192638566",
        "23041379-366e-4ab2-a0db-a18b569bdafb",
        "0f2534da-adad-4dab-a700-8d1493f5ba82",
    ),
    (
        "860ed6da-9864-44e5-b6bf-f06192638566",
        "23b011d4-4cb2-4526-9761-e247d506557a",
        "d8251088-33df-44b9-8286-3e11d80645d1",
    ),
    (
        "860ed6da-9864-44e5-b6bf-f06192638566",
        "46c34c31-2f88-4885-94d2-f973cd3aa963",
        "e92f3626-be91-47da-b197-77e6154f5a15",
    ),
    (
        "860ed6da-9864-44e5-b6bf-f06192638566",
        "46c34c31-2f88-4885-94d2-f973cd3aa963",
        "4092d3b1-67d7-495b-84b4-de224a1b9894",
    ),
    (
        "860ed6da-9864-44e5-b6bf-f06192638566",
        "5a7861e6-948f-451e-8f2e-0c4fc1a2aced",
        "1a4fcf20-634f-4959-bf07-7baef3cbcd55",
    ),
    (
        "860ed6da-9864-44e5-b6bf-f06192638566",
        "5a7861e6-948f-451e-8f2e-0c4fc1a2aced",
        "ff161bca-e057-4045-a3fe-708b6569ab8a",
    ),
    (
        "860ed6da-9864-44e5-b6bf-f06192638566",
        "5a7861e6-948f-451e-8f2e-0c4fc1a2aced",
        "62ca2539-c0c4-4920-aca8-60e8536e725d",
    ),
    (
        "860ed6da-9864-44e5-b6bf-f06192638566",
        "5a7861e6-948f-451e-8f2e-0c4fc1a2aced",
        "85abffe4-0558-462b-b17f-65d8f6ecb910",
    ),
    (
        "860ed6da-9864-44e5-b6bf-f06192638566",
        "5a7861e6-948f-451e-8f2e-0c4fc1a2aced",
        "a033267d-7322-42c8-b011-4015d68b2bc2",
    ),
    (
        "860ed6da-9864-44e5-b6bf-f06192638566",
        "604bab16-64c3-4870-bd2e-52ea93e73e9e",
        "33e934a7-c837-4a28-b896-9e4612a6c810",
    ),
    (
        "860ed6da-9864-44e5-b6bf-f06192638566",
        "79548b0a-9a11-4a9f-bd66-e1aa601a77d8",
        "08bbff19-ce5b-47c1-a680-4cd5d6d8866f",
    ),
    (
        "860ed6da-9864-44e5-b6bf-f06192638566",
        "79548b0a-9a11-4a9f-bd66-e1aa601a77d8",
        "7d39bcf4-6f3d-4daa-914d-6335018fbcf8",
    ),
    (
        "860ed6da-9864-44e5-b6bf-f06192638566",
        "ab2071b5-e299-454a-adf0-f42ac141c936",
        "8b781386-e309-44d5-9b8d-35230f80119a",
    ),
    (
        "860ed6da-9864-44e5-b6bf-f06192638566",
        "cc751338-928a-499a-b1dd-87b9ecc573fd",
        "9445a787-c4cb-4fb2-8a49-1b9947f55876",
    ),
    (
        "be7221c1-f6b2-4bd0-b7ab-bfdd5913d044",
        "1a5bfa7b-999f-42ca-b3a3-3ab238c8abd6",
        "62ca2539-c0c4-4920-aca8-60e8536e725d",
    ),
    (
        "be7221c1-f6b2-4bd0-b7ab-bfdd5913d044",
        "1a5bfa7b-999f-42ca-b3a3-3ab238c8abd6",
        "845518bd-2a56-47c7-92d7-220087939243",
    ),
    (
        "be7221c1-f6b2-4bd0-b7ab-bfdd5913d044",
        "1a5bfa7b-999f-42ca-b3a3-3ab238c8abd6",
        "4ff781dd-8f2e-47ef-91b0-132ecfdee586",
    ),
    (
        "be7221c1-f6b2-4bd0-b7ab-bfdd5913d044",
        "1a5bfa7b-999f-42ca-b3a3-3ab238c8abd6",
        "946381c0-6040-4576-b1c9-dbd9d6a607d1",
    ),
    (
        "be7221c1-f6b2-4bd0-b7ab-bfdd5913d044",
        "23041379-366e-4ab2-a0db-a18b569bdafb",
        "8b1698a3-a055-499c-95e5-56059e3cdd89",
    ),
    (
        "be7221c1-f6b2-4bd0-b7ab-bfdd5913d044",
        "2330705c-290e-4010-9be4-62e7cb5d0477",
        "1f9a5ff0-3394-4895-b45c-089ac6643003",
    ),
    (
        "be7221c1-f6b2-4bd0-b7ab-bfdd5913d044",
        "2330705c-290e-4010-9be4-62e7cb5d0477",
        "62ca2539-c0c4-4920-aca8-60e8536e725d",
    ),
    (
        "be7221c1-f6b2-4bd0-b7ab-bfdd5913d044",
        "2330705c-290e-4010-9be4-62e7cb5d0477",
        "a033267d-7322-42c8-b011-4015d68b2bc2",
    ),
    (
        "be7221c1-f6b2-4bd0-b7ab-bfdd5913d044",
        "affd787b-1e6c-4c9d-a2d4-42d38e9c72b8",
        "845518bd-2a56-47c7-92d7-220087939243",
    ),
    (
        "be7221c1-f6b2-4bd0-b7ab-bfdd5913d044",
        "affd787b-1e6c-4c9d-a2d4-42d38e9c72b8",
        "33e934a7-c837-4a28-b896-9e4612a6c810",
    ),
    (
        "be7221c1-f6b2-4bd0-b7ab-bfdd5913d044",
        "affd787b-1e6c-4c9d-a2d4-42d38e9c72b8",
        "a033267d-7322-42c8-b011-4015d68b2bc2",
    ),
]


def upgrade():
    conn = op.get_bind()

    for library_task_id, library_hazard_id, library_control_id in data:
        conn.execute(
            text(
                f"INSERT INTO library_task_recommendations(library_task_id, library_hazard_id, library_control_id) VALUES ('{library_task_id}','{library_hazard_id}','{library_control_id}') ON CONFLICT (library_task_id, library_hazard_id, library_control_id) DO NOTHING;"
            )
        )


def downgrade():
    pass
