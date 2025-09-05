"""update default data in configurations

Revision ID: e082be3e97bf
Revises: fdde2e696989
Create Date: 2022-09-01 16:04:56.066964

"""
from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "e082be3e97bf"
down_revision = "fdde2e696989"
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

previous_configs = [
    {
        "name": "APP.WORK_PACKAGE.LABELS",
        "config_js": '{"id": "workPackage", "label": "Work Package", "labelPlural": "Work Packages"}',
    },
    {
        "name": "APP.WORK_PACKAGE.ATTRIBUTES",
        "config_js": '{"attributes": [{"id": "name", "label": "Work Package Name", "labelPlural": "Work Package Names", "visible": true, "required": true, "filterable": true, "mappings": null}, {"id": "external_key", "label": "External Key", "labelPlural": "External Keys", "visible": true, "required": true, "filterable": false, "mappings": null}, {"id": "workPackageType", "label": "Work Package Type", "labelPlural": "Work Package Types", "visible": true, "required": true, "filterable": true, "mappings": null}, {"id": "status", "label": "Status", "labelPlural": "Statuses", "visible": true, "required": true, "filterable": false, "mappings": {"pending": ["Pending"], "active": ["active"], "completed": ["completed"]}}, {"id": "prime_contractor", "label": "Prime Contractor", "labelPlural": "Prime Contractor", "visible": true, "required": true, "filterable": true, "mappings": null}, {"id": "other_contractor", "label": "Other Contractor", "labelPlural": "Other Contractors", "visible": true, "required": false, "filterable": false, "mappings": null}, {"id": "start_date", "label": "Start Date", "labelPlural": "Start Dates", "visible": true, "required": true, "filterable": false, "mappings": null}, {"id": "end_date", "label": "End Date", "labelPlural": "End Dates", "visible": true, "required": true, "filterable": false, "mappings": null}, {"id": "division", "label": "Division", "labelPlural": "Divisions", "visible": true, "required": true, "filterable": true, "mappings": null}, {"id": "region", "label": "Region", "labelPlural": "Regions", "visible": true, "required": true, "filterable": true, "mappings": null}, {"id": "zip_code", "label": "Work Package Zip Code", "labelPlural": "Work Package Zip Codes", "visible": true, "required": false, "filterable": false, "mappings": null}, {"id": "description", "label": "Description", "labelPlural": "Descriptions", "visible": true, "required": false, "filterable": false, "mappings": null}, {"id": "asset_type", "label": "Asset Type", "labelPlural": "Asset Types", "visible": true, "required": false, "filterable": false, "mappings": null}, {"id": "project_manager", "label": "Project Manager", "labelPlural": "Project Managers", "visible": true, "required": true, "filterable": false, "mappings": null}, {"id": "primary_assigned_person", "label": "Primary Assigned Person", "labelPlural": "Primary Assigned Persons", "visible": true, "required": true, "filterable": true, "mappings": null}, {"id": "additional_assigned_person", "label": "Additional Assigned Person", "labelPlural": "Additional Assigned Persons", "visible": true, "required": false, "filterable": false, "mappings": null}, {"id": "contract_name", "label": "Contract name", "labelPlural": "Contract names", "visible": true, "required": false, "filterable": false, "mappings": null}, {"id": "contract_reference_number", "label": "Contract Reference Number", "labelPlural": "Contract Reference Numbers", "visible": true, "required": false, "filterable": false, "mappings": null}]}',
    },
    {
        "name": "APP.LOCATION.LABELS",
        "config_js": '{"id": "location", "label": "Location", "labelPlural": "Locations"}',
    },
    {
        "name": "APP.LOCATION.ATTRIBUTES",
        "config_js": '{"attributes": [{"id": "name", "label": "Location Name", "labelPlural": "Location Names", "visible": true, "required": true, "filterable": true, "mappings": null}, {"id": "primary_assigned_person", "label": "Primary Assigned Person", "labelPlural": "Primary Assigned Persons", "visible": true, "required": true, "filterable": true, "mappings": null}, {"id": "additional_assigned_person", "label": "Additional Assigned Person", "labelPlural": "Additional Assigned Persons", "visible": true, "required": false, "filterable": false, "mappings": null}]}',
    },
    {
        "name": "APP.ACTIVITY.LABELS",
        "config_js": '{"id": "activity", "label": "Activity", "labelPlural": "Activities"}',
    },
    {
        "name": "APP.ACTIVITY.ATTRIBUTES",
        "config_js": empty_attributes_js,
    },
    {
        "name": "APP.TASK.LABELS",
        "config_js": '{"id": "task", "label": "Task", "labelPlural": "Tasks"}',
    },
    {
        "name": "APP.TASK.ATTRIBUTES",
        "config_js": empty_attributes_js,
    },
    {
        "name": "APP.SITE_CONDITION.LABELS",
        "config_js": '{"id": "siteCondition", "label": "Site Condition", "labelPlural": "Site Conditions"}',
    },
    {
        "name": "APP.SITE_CONDITION.ATTRIBUTES",
        "config_js": empty_attributes_js,
    },
    {
        "name": "APP.HAZARD.LABELS",
        "config_js": '{"id": "hazard", "label": "Hazard", "labelPlural": "Hazards"}',
    },
    {
        "name": "APP.HAZARD.ATTRIBUTES",
        "config_js": empty_attributes_js,
    },
    {
        "name": "APP.CONTROL.LABELS",
        "config_js": '{"id": "control", "label": "Control", "labelPlural": "Controls"}',
    },
    {
        "name": "APP.CONTROL.ATTRIBUTES",
        "config_js": empty_attributes_js,
    },
]

delete_query = """
        DELETE FROM public.configurations WHERE name = :name and value = :config_js and tenant_id is null;
    """
insert_query = """
    INSERT INTO public.configurations(name, tenant_id, value) VALUES (:name, null, :config_js);
    """


def upgrade():
    conn = op.get_bind()
    for config in previous_configs:
        conn.execute(text(delete_query), config)

    for config in configs_to_store:
        conn.execute(text(insert_query), config)


def downgrade():
    conn = op.get_bind()
    for config in configs_to_store:
        conn.execute(text(delete_query), config)
    for config in previous_configs:
        conn.execute(text(insert_query), config)
