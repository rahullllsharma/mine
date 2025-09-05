"""Fix duplicated supervisors

Revision ID: 09d92d29b122
Revises: f264f41cb18b
Create Date: 2022-09-06 17:29:28.509772

"""
from collections import defaultdict
from uuid import UUID

from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "09d92d29b122"
down_revision = "f264f41cb18b"
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()

    # Find duplicated supervisors
    tenant_items: defaultdict[
        tuple[UUID, str], list[tuple[UUID | None, UUID]]
    ] = defaultdict(list)
    for item in connection.execute(
        text(
            """
            SELECT s.*
            FROM (SELECT tenant_id, name from supervisor group by tenant_id, name having count(id) > 1) x, supervisor s
            WHERE x.tenant_id = s.tenant_id and x.name = s.name
            """
        )
    ).fetchall():
        tenant_items[(item.tenant_id, item.name)].append((item.user_id, item.id))

    # Migrate duplicated supervisors
    duplicated_ids: list[UUID] = []
    for items in tenant_items.values():
        # Set items with user_id defined as first on the list
        items.sort(key=lambda i: bool(i[0]), reverse=True)

        _, keep_id = items.pop(0)
        duplicated_ids.extend(i[1] for i in items)
        ids_str = "', '".join(str(i[1]) for i in items)
        connection.execute(
            text(
                f"UPDATE incidents SET supervisor_id = '{keep_id}' WHERE supervisor_id IN ('{ids_str}')"
            ),
        )
        connection.execute(
            text(
                f"UPDATE observations SET supervisor_id = '{keep_id}' WHERE supervisor_id IN ('{ids_str}')"
            ),
        )

    # Remove duplicated supervisors
    if duplicated_ids:
        ids_str = "', '".join(map(str, duplicated_ids))
        connection.execute(
            text(f"DELETE FROM supervisor WHERE id IN ('{ids_str}')"),
        )

    # Make sure we dont duplicate supervisor in the future
    op.create_unique_constraint(
        "supervisor_unique_name", "supervisor", ["tenant_id", "name"]
    )


def downgrade():
    op.drop_constraint("supervisor_unique_name", "supervisor", type_="unique")
