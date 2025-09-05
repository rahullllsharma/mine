"""Recreate configurations table

Revision ID: 7e98f0dc21b4
Revises: e082be3e97bf
Create Date: 2022-08-31 14:37:27.669330

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op
from sqlalchemy import text
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "7e98f0dc21b4"
down_revision = "e082be3e97bf"
branch_labels = None
depends_on = None


empty_attributes_js = '{"attributes": []}'
configs_to_store = [
    {
        "name": "APP.WORK_PACKAGE.LABELS",
        "config_js": '{"key": "workPackage", "label": "Work Package", "labelPlural": "Work Packages"}',
    },
    {
        "name": "APP.WORK_PACKAGE.ATTRIBUTES",
        "config_js": '{"attributes": [{"key": "name", "label": "Work Package Name", "labelPlural": "Work Package Names", "visible": true, "required": true, "filterable": true, "mappings": null}, {"key": "externalKey", "label": "External Key", "labelPlural": "External Keys", "visible": true, "required": true, "filterable": false, "mappings": null}, {"key": "workPackageType", "label": "Work Package Type", "labelPlural": "Work Package Types", "visible": true, "required": true, "filterable": true, "mappings": null}, {"key": "status", "label": "Status", "labelPlural": "Statuses", "visible": true, "required": true, "filterable": false, "mappings": {"pending": ["Pending"], "active": ["active"], "completed": ["completed"]}}, {"key": "primeContractor", "label": "Prime Contractor", "labelPlural": "Prime Contractor", "visible": true, "required": true, "filterable": true, "mappings": null}, {"key": "otherContractor", "label": "Other Contractor", "labelPlural": "Other Contractors", "visible": true, "required": false, "filterable": false, "mappings": null}, {"key": "startDate", "label": "Start Date", "labelPlural": "Start Dates", "visible": true, "required": true, "filterable": false, "mappings": null}, {"key": "endDate", "label": "End Date", "labelPlural": "End Dates", "visible": true, "required": true, "filterable": false, "mappings": null}, {"key": "division", "label": "Division", "labelPlural": "Divisions", "visible": true, "required": true, "filterable": true, "mappings": null}, {"key": "region", "label": "Region", "labelPlural": "Regions", "visible": true, "required": true, "filterable": true, "mappings": null}, {"key": "zipCode", "label": "Work Package Zip Code", "labelPlural": "Work Package Zip Codes", "visible": true, "required": false, "filterable": false, "mappings": null}, {"key": "description", "label": "Description", "labelPlural": "Descriptions", "visible": true, "required": false, "filterable": false, "mappings": null}, {"key": "assetType", "label": "Asset Type", "labelPlural": "Asset Types", "visible": true, "required": false, "filterable": false, "mappings": null}, {"key": "projectManager", "label": "Project Manager", "labelPlural": "Project Managers", "visible": true, "required": true, "filterable": false, "mappings": null}, {"key": "primaryAssignedPerson", "label": "Primary Assigned Person", "labelPlural": "Primary Assigned Persons", "visible": true, "required": true, "filterable": true, "mappings": null}, {"key": "additionalAssignedPerson", "label": "Additional Assigned Person", "labelPlural": "Additional Assigned Persons", "visible": true, "required": false, "filterable": false, "mappings": null}, {"key": "contractName", "label": "Contract name", "labelPlural": "Contract names", "visible": true, "required": false, "filterable": false, "mappings": null}, {"key": "contractReferenceNumber", "label": "Contract Reference Number", "labelPlural": "Contract Reference Numbers", "visible": true, "required": false, "filterable": false, "mappings": null}]}',
    },
    {
        "name": "APP.LOCATION.LABELS",
        "config_js": '{"key": "location", "label": "Location", "labelPlural": "Locations"}',
    },
    {
        "name": "APP.LOCATION.ATTRIBUTES",
        "config_js": '{"attributes": [{"key": "name", "label": "Location Name", "labelPlural": "Location Names", "visible": true, "required": true, "filterable": true, "mappings": null}, {"key": "primaryAssignedPerson", "label": "Primary Assigned Person", "labelPlural": "Primary Assigned Persons", "visible": true, "required": true, "filterable": true, "mappings": null}, {"key": "additionalAssignedPerson", "label": "Additional Assigned Person", "labelPlural": "Additional Assigned Persons", "visible": true, "required": false, "filterable": false, "mappings": null}]}',
    },
    {
        "name": "APP.ACTIVITY.LABELS",
        "config_js": '{"key": "activity", "label": "Activity", "labelPlural": "Activities"}',
    },
    {
        "name": "APP.ACTIVITY.ATTRIBUTES",
        "config_js": empty_attributes_js,
    },
    {
        "name": "APP.TASK.LABELS",
        "config_js": '{"key": "task", "label": "Task", "labelPlural": "Tasks"}',
    },
    {
        "name": "APP.TASK.ATTRIBUTES",
        "config_js": empty_attributes_js,
    },
    {
        "name": "APP.SITE_CONDITION.LABELS",
        "config_js": '{"key": "siteCondition", "label": "Site Condition", "labelPlural": "Site Conditions"}',
    },
    {
        "name": "APP.SITE_CONDITION.ATTRIBUTES",
        "config_js": empty_attributes_js,
    },
    {
        "name": "APP.HAZARD.LABELS",
        "config_js": '{"key": "hazard", "label": "Hazard", "labelPlural": "Hazards"}',
    },
    {
        "name": "APP.HAZARD.ATTRIBUTES",
        "config_js": empty_attributes_js,
    },
    {
        "name": "APP.CONTROL.LABELS",
        "config_js": '{"key": "control", "label": "Control", "labelPlural": "Controls"}',
    },
    {
        "name": "APP.CONTROL.ATTRIBUTES",
        "config_js": empty_attributes_js,
    },
]

insert_query = """
    INSERT INTO public.configurations(name, tenant_id, value) VALUES (:name, null, :config_js);
    """


def upgrade():
    op.drop_table("configurations")
    op.execute("DROP SEQUENCE IF EXISTS configurations_id_seq")
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
    op.create_table(
        "configurations",
        sa.Column("id", postgresql.UUID(), nullable=True),
        sa.Column("name", sa.VARCHAR(), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(), nullable=True),
        sa.Column("value", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(
            ["tenant_id"], ["tenants.id"], name="configurations_tenant_id_fkey"
        ),
        sa.UniqueConstraint("name", "tenant_id", name="u_name_tenant_1"),
    )

    conn = op.get_bind()
    for config in configs_to_store:
        conn.execute(text(insert_query), config)
    op.execute("UPDATE configurations set id=uuid_generate_v4();")
    op.alter_column("configurations", "id", nullable=False, primary_key=True)


def downgrade():
    op.execute("CREATE SEQUENCE IF NOT EXISTS configurations_id_seq")
    op.drop_table("configurations")
    op.create_table(
        "configurations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=True),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("tenant_id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
        sa.Column("value", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
        ),
        sa.UniqueConstraint("name", "tenant_id", name="u_name_tenant_1"),
    )
    conn = op.get_bind()
    for config in configs_to_store:
        conn.execute(text(insert_query), config)
    op.execute("UPDATE configurations set id=nextval('configurations_id_seq')")
    op.alter_column("configurations", "id", nullable=False, primary_key=True)
