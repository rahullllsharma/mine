"""update project status casing

Revision ID: 93832a977078
Revises: 3f61b28ec57d
Create Date: 2022-09-13 14:05:52.893907

"""
from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "93832a977078"
down_revision = "802f52ea733b"
branch_labels = None
depends_on = None


new_values = {
    "config_js": '{"attributes": [{"key": "name", "label": "Work Package Name", "labelPlural": "Work Package Names", "visible": true, "required": true, "filterable": true, "mappings": null}, {"key": "externalKey", "label": "External Key", "labelPlural": "External Keys", "visible": true, "required": true, "filterable": false, "mappings": null}, {"key": "workPackageType", "label": "Work Package Type", "labelPlural": "Work Package Types", "visible": true, "required": true, "filterable": true, "mappings": null}, {"key": "status", "label": "Status", "labelPlural": "Statuses", "visible": true, "required": true, "filterable": false, "mappings": {"pending": ["Pending"], "active": ["Active"], "completed": ["Completed"]}}, {"key": "primeContractor", "label": "Prime Contractor", "labelPlural": "Prime Contractor", "visible": true, "required": true, "filterable": true, "mappings": null}, {"key": "otherContractor", "label": "Other Contractor", "labelPlural": "Other Contractors", "visible": true, "required": false, "filterable": false, "mappings": null}, {"key": "startDate", "label": "Start Date", "labelPlural": "Start Dates", "visible": true, "required": true, "filterable": false, "mappings": null}, {"key": "endDate", "label": "End Date", "labelPlural": "End Dates", "visible": true, "required": true, "filterable": false, "mappings": null}, {"key": "division", "label": "Division", "labelPlural": "Divisions", "visible": true, "required": true, "filterable": true, "mappings": null}, {"key": "region", "label": "Region", "labelPlural": "Regions", "visible": true, "required": true, "filterable": true, "mappings": null}, {"key": "zipCode", "label": "Work Package Zip Code", "labelPlural": "Work Package Zip Codes", "visible": true, "required": false, "filterable": false, "mappings": null}, {"key": "description", "label": "Description", "labelPlural": "Descriptions", "visible": true, "required": false, "filterable": false, "mappings": null}, {"key": "assetType", "label": "Asset Type", "labelPlural": "Asset Types", "visible": true, "required": false, "filterable": false, "mappings": null}, {"key": "projectManager", "label": "Project Manager", "labelPlural": "Project Managers", "visible": true, "required": true, "filterable": false, "mappings": null}, {"key": "primaryAssignedPerson", "label": "Primary Assigned Person", "labelPlural": "Primary Assigned Persons", "visible": true, "required": true, "filterable": true, "mappings": null}, {"key": "additionalAssignedPerson", "label": "Additional Assigned Person", "labelPlural": "Additional Assigned Persons", "visible": true, "required": false, "filterable": false, "mappings": null}, {"key": "contractName", "label": "Contract Name", "labelPlural": "Contract names", "visible": true, "required": false, "filterable": false, "mappings": null}, {"key": "contractReferenceNumber", "label": "Contract Reference Number", "labelPlural": "Contract Reference Numbers", "visible": true, "required": false, "filterable": false, "mappings": null}]}'
}

old_values = {
    "config_js": '{"attributes": [{"key": "name", "label": "Work Package Name", "labelPlural": "Work Package Names", "visible": true, "required": true, "filterable": true, "mappings": null}, {"key": "externalKey", "label": "External Key", "labelPlural": "External Keys", "visible": true, "required": true, "filterable": false, "mappings": null}, {"key": "workPackageType", "label": "Work Package Type", "labelPlural": "Work Package Types", "visible": true, "required": true, "filterable": true, "mappings": null}, {"key": "status", "label": "Status", "labelPlural": "Statuses", "visible": true, "required": true, "filterable": false, "mappings": {"pending": ["Pending"], "active": ["active"], "completed": ["completed"]}}, {"key": "primeContractor", "label": "Prime Contractor", "labelPlural": "Prime Contractor", "visible": true, "required": true, "filterable": true, "mappings": null}, {"key": "otherContractor", "label": "Other Contractor", "labelPlural": "Other Contractors", "visible": true, "required": false, "filterable": false, "mappings": null}, {"key": "startDate", "label": "Start Date", "labelPlural": "Start Dates", "visible": true, "required": true, "filterable": false, "mappings": null}, {"key": "endDate", "label": "End Date", "labelPlural": "End Dates", "visible": true, "required": true, "filterable": false, "mappings": null}, {"key": "division", "label": "Division", "labelPlural": "Divisions", "visible": true, "required": true, "filterable": true, "mappings": null}, {"key": "region", "label": "Region", "labelPlural": "Regions", "visible": true, "required": true, "filterable": true, "mappings": null}, {"key": "zipCode", "label": "Work Package Zip Code", "labelPlural": "Work Package Zip Codes", "visible": true, "required": false, "filterable": false, "mappings": null}, {"key": "description", "label": "Description", "labelPlural": "Descriptions", "visible": true, "required": false, "filterable": false, "mappings": null}, {"key": "assetType", "label": "Asset Type", "labelPlural": "Asset Types", "visible": true, "required": false, "filterable": false, "mappings": null}, {"key": "projectManager", "label": "Project Manager", "labelPlural": "Project Managers", "visible": true, "required": true, "filterable": false, "mappings": null}, {"key": "primaryAssignedPerson", "label": "Primary Assigned Person", "labelPlural": "Primary Assigned Persons", "visible": true, "required": true, "filterable": true, "mappings": null}, {"key": "additionalAssignedPerson", "label": "Additional Assigned Person", "labelPlural": "Additional Assigned Persons", "visible": true, "required": false, "filterable": false, "mappings": null}, {"key": "contractName", "label": "Contract name", "labelPlural": "Contract names", "visible": true, "required": false, "filterable": false, "mappings": null}, {"key": "contractReferenceNumber", "label": "Contract Reference Number", "labelPlural": "Contract Reference Numbers", "visible": true, "required": false, "filterable": false, "mappings": null}]}'
}

update_query = """
    UPDATE configurations set value=:config_js where tenant_id is null and name='APP.WORK_PACKAGE.ATTRIBUTES'
"""


def upgrade():
    conn = op.get_bind()
    conn.execute(text(update_query), new_values)


def downgrade():
    conn = op.get_bind()
    conn.execute(text(update_query), old_values)
