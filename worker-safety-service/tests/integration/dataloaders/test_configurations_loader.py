import pytest

from tests.factories import TenantFactory
from tests.integration.dataloaders.conftest import LoaderFactory
from worker_safety_service.dal.configurations import (
    WORK_PACKAGE_CONFIG,
    AttributeConfigurationExt,
    EntityConfiguration,
    EntityConfigurationExt,
)
from worker_safety_service.graphql.data_loaders.configurations import (
    TenantConfigurationsLoader,
)
from worker_safety_service.models import AsyncSession

data_in_json = """
{
    "key": "workPackage",
    "label": "Work Package",
    "labelPlural": "Work Packages",
    "attributes": [
        {
            "key": "name",
            "label": "Work Package Name",
            "labelPlural": "Work Package Names",
            "visible": true,
            "required": true,
            "filterable": true
        },
        {
            "key": "externalKey",
            "label": "External Key",
            "labelPlural": "External Keys",
            "visible": true,
            "required": true,
            "filterable": false
        },
        {
            "key": "workPackageType",
            "label": "Work Package Type",
            "labelPlural": "Work Package Types",
            "visible": true,
            "required": true,
            "filterable": true
        },
        {
            "key": "status",
            "label": "Status",
            "labelPlural": "Statuses",
            "visible": true,
            "required": true,
            "filterable": false,
            "mappings": {
                "pending": [
                    "Pending"
                ],
                "active": [
                    "Active"
                ],
                "completed": [
                    "Completed"
                ]
            }
        },
        {
            "key": "primeContractor",
            "label": "Prime Contractor",
            "labelPlural": "Prime Contractor",
            "visible": true,
            "required": true,
            "filterable": true
        },
        {
            "key": "otherContractor",
            "label": "Other Contractor",
            "labelPlural": "Other Contractors",
            "visible": true,
            "required": false,
            "filterable": false
        },
        {
            "key": "startDate",
            "label": "Start Date",
            "labelPlural": "Start Dates",
            "visible": true,
            "required": true,
            "filterable": false
        },
        {
            "key": "endDate",
            "label": "End Date",
            "labelPlural": "End Dates",
            "visible": true,
            "required": true,
            "filterable": false
        },
        {
            "key": "division",
            "label": "Division",
            "labelPlural": "Divisions",
            "visible": true,
            "required": true,
            "filterable": true
        },
        {
            "key": "region",
            "label": "Region",
            "labelPlural": "Regions",
            "visible": true,
            "required": true,
            "filterable": true
        },
        {
            "key": "zipCode",
            "label": "Work Package Zip Code",
            "labelPlural": "Work Package Zip Codes",
            "visible": true,
            "required": false,
            "filterable": false
        },
        {
            "key": "description",
            "label": "Description",
            "labelPlural": "Descriptions",
            "visible": true,
            "required": false,
            "filterable": false
        },
        {
            "key": "assetType",
            "label": "Asset Type",
            "labelPlural": "Asset Types",
            "visible": true,
            "required": false,
            "filterable": false
        },
        {
            "key": "projectManager",
            "label": "Project Manager",
            "labelPlural": "Project Managers",
            "visible": true,
            "required": true,
            "filterable": false
        },
        {
            "key": "primaryAssignedPerson",
            "label": "Primary Assigned Person",
            "labelPlural": "Primary Assigned Persons",
            "visible": true,
            "required": true,
            "filterable": true
        },
        {
            "key": "additionalAssignedPerson",
            "label": "Additional Assigned Person",
            "labelPlural": "Additional Assigned Persons",
            "visible": true,
            "required": false,
            "filterable": false
        },
        {
            "key": "contractName",
            "label": "Contract Name",
            "labelPlural": "Contract names",
            "visible": true,
            "required": false,
            "filterable": false
        },
        {
            "key": "contractReferenceNumber",
            "label": "Contract Reference Number",
            "labelPlural": "Contract Reference Numbers",
            "visible": true,
            "required": false,
            "filterable": false
        }
    ]
}
"""


# TODO: Parametrize
@pytest.mark.asyncio
@pytest.mark.integration
async def test_read_after_write(
    db_session: AsyncSession,
    configurations_loader_factory: LoaderFactory[TenantConfigurationsLoader],
) -> None:
    my_tenant_id = (await TenantFactory.default_tenant(db_session)).id
    loader = configurations_loader_factory(my_tenant_id)

    configs: EntityConfiguration = EntityConfiguration.parse_raw(data_in_json)
    default_configs = configs.copy()
    default_configs.label += " Default"
    default_configs.labelPlural += " Default"

    await loader.update_default_section(default_configs)
    await loader.update_section(configs)
    actual_configs = await loader.get_section(WORK_PACKAGE_CONFIG)

    assert configs.attributes
    assert default_configs.attributes

    expected_attributes = []
    for attr, default_attr in zip(configs.attributes, default_configs.attributes):
        expected_attr = AttributeConfigurationExt(
            **attr.dict(),
            defaultLabel=default_attr.label,
            defaultLabelPlural=default_attr.labelPlural,
        )
        expected_attributes.append(expected_attr)

    expected = EntityConfigurationExt(
        key=configs.key,
        label=configs.label,
        labelPlural=configs.labelPlural,
        defaultLabel=default_configs.label,
        defaultLabelPlural=default_configs.labelPlural,
    )
    actual_configs.attributes = None
    assert actual_configs == expected
