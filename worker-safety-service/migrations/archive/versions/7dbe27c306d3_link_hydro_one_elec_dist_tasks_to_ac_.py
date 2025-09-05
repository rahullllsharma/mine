"""link_hydro_one_elec_dist_tasks_to_ac_group

Revision ID: 7dbe27c306d3
Revises: 795d1a2b2db0
Create Date: 2022-10-12 14:27:27.170337

"""

from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "7dbe27c306d3"
down_revision = "795d1a2b2db0"
branch_labels = None
depends_on = None

library_task_activity_type_relations = [
    ("524bcf3a-1ddb-4b2d-91e6-97013241689b", "f8e7acfa-cc2d-46f2-9100-2a82a01654d5"),
    ("524bcf3a-1ddb-4b2d-91e6-97013241689b", "7ebf6ae3-0cbe-455c-a677-396b132c0563"),
    ("524bcf3a-1ddb-4b2d-91e6-97013241689b", "68d4fe67-2873-42c1-81cf-38d941b365d8"),
    ("314350b9-79e3-43ea-8167-4ede2a4eca4a", "61584f3f-39ca-4968-b1f9-75df32e5ad42"),
    ("6cd56ae8-b45f-4ebc-9e7f-5a0e4e705472", "707c89f3-69f5-44ef-855d-1285c37bc19b"),
    ("524bcf3a-1ddb-4b2d-91e6-97013241689b", "e76ac93a-3460-40e0-9c67-2ba771be2306"),
    ("1f8e5b52-31dc-45e7-8b50-cdf0fd0a3223", "47946e56-d353-4d09-ba02-948403fe4acc"),
    ("1e4c6c0a-c675-4be0-a451-2692467fd25a", "f422cab2-a7be-4015-80d4-ddfc2a30e717"),
    ("1e4c6c0a-c675-4be0-a451-2692467fd25a", "527054e9-88e8-44e9-b006-f72eb7934436"),
    ("1e4c6c0a-c675-4be0-a451-2692467fd25a", "58e446e5-f278-4a65-aea1-a1e2604da5bb"),
    ("1e4c6c0a-c675-4be0-a451-2692467fd25a", "b7975a77-1cc9-45c4-8e90-9173f2e2ce5f"),
    ("1e4c6c0a-c675-4be0-a451-2692467fd25a", "8fa3aba3-66fe-41ea-b315-ba070785bbcf"),
    ("1e4c6c0a-c675-4be0-a451-2692467fd25a", "831d5978-5338-449b-97b1-feededfa0238"),
    ("1e4c6c0a-c675-4be0-a451-2692467fd25a", "1867f569-da9d-4428-8081-189b9ff10c60"),
    ("1e4c6c0a-c675-4be0-a451-2692467fd25a", "3ddc633b-f712-4f39-aa6b-ababefb6fbce"),
    ("1e4c6c0a-c675-4be0-a451-2692467fd25a", "598bf4fd-4c5f-4bce-919b-1aa56929f4b8"),
    ("c0d44bd5-d17c-4d45-9452-dc195e432e71", "92ca4761-59c8-4682-96f1-e4942f1dc400"),
    ("1f8e5b52-31dc-45e7-8b50-cdf0fd0a3223", "065b1971-6107-4e99-b84b-a44662262866"),
    ("6c26e14a-43ca-4657-af27-65df8d630e59", "abf3d9dc-2de8-4ea5-9f26-16c3b1fd55a5"),
    ("00ef4058-ad6e-4781-ae1e-4fcd72839e32", "ba3283c2-4a73-4306-bc01-ecb61a69b982"),
    ("6c26e14a-43ca-4657-af27-65df8d630e59", "a5ae7d47-0f09-4636-9d96-b998b62f8f5d"),
    ("6c26e14a-43ca-4657-af27-65df8d630e59", "ba622c1d-dee9-4b51-a0e4-d98acefd1092"),
    ("b5d41b25-58c6-4b0d-9f31-1d3df4ce5ce4", "1b6fad18-62cc-4eec-af79-fba6bcb65cdd"),
    ("b5d41b25-58c6-4b0d-9f31-1d3df4ce5ce4", "a27c5ce6-d0ba-428f-af2e-1b01768df242"),
    ("1e4c6c0a-c675-4be0-a451-2692467fd25a", "7da1893e-0657-4c7c-ab14-043f3f731691"),
    ("1e4c6c0a-c675-4be0-a451-2692467fd25a", "4643f8d2-0379-4119-b30e-10086ce2bc14"),
    ("1e4c6c0a-c675-4be0-a451-2692467fd25a", "f5304c43-efbb-4767-84ba-a679c428b0d1"),
    ("b5d41b25-58c6-4b0d-9f31-1d3df4ce5ce4", "43974f5a-8576-49e4-a2b3-7c2caa56b8e2"),
    ("1e4c6c0a-c675-4be0-a451-2692467fd25a", "65f285d4-cf2f-4ff5-b490-1deeeea38d94"),
    ("1e4c6c0a-c675-4be0-a451-2692467fd25a", "2b09776f-7c33-46e9-b90c-e28df4320e49"),
    ("1e4c6c0a-c675-4be0-a451-2692467fd25a", "e9ba4860-d0c2-4b84-a4af-4d2b29dc8da3"),
    ("1e4c6c0a-c675-4be0-a451-2692467fd25a", "e57a4ddb-dec3-4aac-836b-b5661428d788"),
    ("1e4c6c0a-c675-4be0-a451-2692467fd25a", "0d43e37f-0c51-4315-9dc4-56d0c6028bba"),
    ("1e4c6c0a-c675-4be0-a451-2692467fd25a", "e95730a6-1ca7-4582-95f3-d0fca91644f7"),
    ("1e4c6c0a-c675-4be0-a451-2692467fd25a", "3ccbb149-9243-4377-835c-c2ffb7963775"),
    ("1e4c6c0a-c675-4be0-a451-2692467fd25a", "744eaba2-7220-4ce1-9b0c-eb1850898926"),
    ("1e4c6c0a-c675-4be0-a451-2692467fd25a", "c28d58f4-d149-4970-b224-7c6350b03972"),
    ("1e4c6c0a-c675-4be0-a451-2692467fd25a", "002ddb94-2cc9-4fb5-92a9-76d6f2581e31"),
    ("1e4c6c0a-c675-4be0-a451-2692467fd25a", "33cb8b7f-fd2f-4b3a-b253-e04c1cc10b27"),
]


def upgrade():
    conn = op.get_bind()
    for activity_group_id, library_task_id in library_task_activity_type_relations:
        conn.execute(
            text(
                f"INSERT INTO library_task_activity_groups (activity_group_id, library_task_id) VALUES ('{activity_group_id}', '{library_task_id}') ON CONFLICT DO NOTHING;"
            )
        )


def downgrade():
    pass
