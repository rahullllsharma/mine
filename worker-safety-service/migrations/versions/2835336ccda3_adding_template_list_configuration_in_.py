"""Adding Template list configuration in admin

Revision ID: 2835336ccda3
Revises: 7a5cf66a8c85
Create Date: 2025-03-24 17:53:53.634670

"""
import uuid

from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "2835336ccda3"
down_revision = "7a5cf66a8c85"
branch_labels = None
depends_on = None

configs_to_store = (
    {
        "id": uuid.uuid4(),
        "name": "APP.TEMPLATE_FORM.LABELS",
        "value": '{"key": "templateForm", "label": "Template Form", "labelPlural": "Template Forms"}',
    },
    {
        "id": uuid.uuid4(),
        "name": "APP.TEMPLATE_FORM.ATTRIBUTES",
        "value": '{"attributes": []}',
    },
)


def upgrade() -> None:
    insert_query = """
    INSERT INTO public.configurations(id,name, tenant_id, value) VALUES (:id, :name, null, :value);
    """
    conn = op.get_bind()
    for config in configs_to_store:
        conn.execute(text(insert_query), config)


def downgrade() -> None:
    delete_query = """
    DELETE FROM public.configurations WHERE name = :name and value = :value and tenant_id is null;
    """

    conn = op.get_bind()
    for config in configs_to_store:
        conn.execute(text(delete_query), config)
