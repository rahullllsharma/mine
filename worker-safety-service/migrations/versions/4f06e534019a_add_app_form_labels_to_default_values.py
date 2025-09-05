"""Add APP.FORM.LABELS to default values

Revision ID: 4f06e534019a
Revises: 82c53cce39a8
Create Date: 2023-08-08 16:17:51.505179

"""
import uuid

from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "4f06e534019a"
down_revision = "82c53cce39a8"
branch_labels = None
depends_on = None

forms_default_config = (
    {
        "id": uuid.uuid4(),
        "name": "APP.FORM_LIST.LABELS",
        "value": '{"key": "formList", "label": "Form List", "labelPlural": "Forms List"}',
    },
    {
        "id": uuid.uuid4(),
        "name": "APP.FORM_LIST.ATTRIBUTES",
        "value": '{"attributes": [{"key": "formName", "label": "Form Name", "labelPlural": "Form Names", "visible": false, "required": false, "filterable": false, "mappings": null}, {"key": "location", "label": "Location", "labelPlural": "Locations", "visible": false, "required": false, "filterable": false, "mappings": null}, {"key": "status", "label": "Status", "labelPlural": "Statuses", "visible": false, "required": false, "filterable": false, "mappings": null}, {"key": "workPackage", "label": "Work Package", "labelPlural": "Work Packages", "visible": false, "required": false, "filterable": false, "mappings": null}, {"key": "createdBy", "label": "Created By", "labelPlural": "Created By", "visible": false, "required": false, "filterable": false, "mappings": null}, {"key": "createdOn", "label": "Created On", "labelPlural": "Created On", "visible": false, "required": false, "filterable": false, "mappings": null}]}',
    },
)


def upgrade():
    conn = op.get_bind()

    count_query = text(
        "SELECT COUNT(*) FROM public.configurations WHERE name = :name and tenant_id is NULL;"
    )
    insert_query = text(
        "INSERT INTO public.configurations (id, name, value) VALUES (:id, :name, :value)"
    )

    form_label_records_found = conn.scalar(count_query, forms_default_config[0])
    if form_label_records_found == 0:
        conn.execute(insert_query, forms_default_config)

    form_attribute_records_found = conn.scalar(count_query, forms_default_config[1])
    if form_attribute_records_found == 0:
        conn.execute(insert_query, forms_default_config)


def downgrade():
    pass
