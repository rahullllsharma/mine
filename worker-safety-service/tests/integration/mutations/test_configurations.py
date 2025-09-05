import json

import pytest
from fastapi.encoders import jsonable_encoder

from tests.integration.conftest import ExecuteGQL
from worker_safety_service.dal.configurations import (
    ENTITY_SCHEMAS,
    ConfigurationsManager,
)

work_package_config = {
    "key": "workPackage",
    "label": "Work Package",
    "labelPlural": "Work Packages",
    "attributes": [
        {
            "key": "name",
            "label": "The Work Unit Thingy",
            "labelPlural": "Work Package Names",
            "visible": True,
            "required": True,
            "filterable": True,
            "mappings": None,
        },
        {
            "key": "externalKey",
            "label": "External Key",
            "labelPlural": "External Keys",
            "visible": True,
            "required": True,
            "filterable": False,
            "mappings": None,
        },
        {
            "key": "workPackageType",
            "label": "Work Package Type",
            "labelPlural": "Work Package Types",
            "visible": True,
            "required": True,
            "filterable": True,
            "mappings": None,
        },
        {
            "key": "status",
            "label": "Status",
            "labelPlural": "Statuses",
            "visible": True,
            "required": True,
            "filterable": False,
            "mappings": {
                "pending": ["Pending"],
                "active": ["Active"],
                "completed": ["Completed"],
            },
        },
        {
            "key": "primeContractor",
            "label": "Prime Contractor",
            "labelPlural": "Prime Contractor",
            "visible": True,
            "required": True,
            "filterable": True,
            "mappings": None,
        },
        {
            "key": "otherContractor",
            "label": "Other Contractor",
            "labelPlural": "Other Contractors",
            "visible": True,
            "required": False,
            "filterable": False,
            "mappings": None,
        },
        {
            "key": "startDate",
            "label": "Start Date",
            "labelPlural": "Start Dates",
            "visible": True,
            "required": True,
            "filterable": False,
            "mappings": None,
        },
        {
            "key": "endDate",
            "label": "End Date",
            "labelPlural": "End Dates",
            "visible": True,
            "required": True,
            "filterable": False,
            "mappings": None,
        },
        {
            "key": "division",
            "label": "Division",
            "labelPlural": "Divisions",
            "visible": True,
            "required": True,
            "filterable": True,
            "mappings": None,
        },
        {
            "key": "region",
            "label": "Region",
            "labelPlural": "Regions",
            "visible": True,
            "required": True,
            "filterable": True,
            "mappings": None,
        },
        {
            "key": "zipCode",
            "label": "Work Package Zip Code",
            "labelPlural": "Work Package Zip Codes",
            "visible": True,
            "required": False,
            "filterable": False,
            "mappings": None,
        },
        {
            "key": "description",
            "label": "Description",
            "labelPlural": "Descriptions",
            "visible": True,
            "required": False,
            "filterable": False,
            "mappings": None,
        },
        {
            "key": "assetType",
            "label": "Asset Type",
            "labelPlural": "Asset Types",
            "visible": True,
            "required": False,
            "filterable": False,
            "mappings": None,
        },
        {
            "key": "projectManager",
            "label": "Project Manager",
            "labelPlural": "Project Managers",
            "visible": True,
            "required": True,
            "filterable": False,
            "mappings": None,
        },
        {
            "key": "primaryAssignedPerson",
            "label": "Primary Assigned Person",
            "labelPlural": "Primary Assigned Persons",
            "visible": True,
            "required": True,
            "filterable": True,
            "mappings": None,
        },
        {
            "key": "additionalAssignedPerson",
            "label": "Additional Assigned Person",
            "labelPlural": "Additional Assigned Persons",
            "visible": True,
            "required": False,
            "filterable": False,
            "mappings": None,
        },
        {
            "key": "contractName",
            "label": "Contract Name",
            "labelPlural": "Contract names",
            "visible": True,
            "required": False,
            "filterable": False,
            "mappings": None,
        },
        {
            "key": "contractReferenceNumber",
            "label": "Contract Reference Number",
            "labelPlural": "Contract Reference Numbers",
            "visible": True,
            "required": False,
            "filterable": False,
            "mappings": None,
        },
    ],
}

missing_required_fields_config = {
    "key": "workPackage",
    "label": "Work Package",
    "labelPlural": "Work Packages",
    "attributes": [
        {
            "key": "name",
            "label": "Work Package Name",
            "labelPlural": "Work Package Names",
            "visible": True,
            "required": True,
            "filterable": True,
        },
        {
            "key": "externalKey",
            "label": "External Key",
            "labelPlural": "External Keys",
            "visible": True,
            "required": True,
            "filterable": False,
        },
    ],
}

mandatory_variables_not_visible = {
    "key": "location",
    "label": "Location",
    "labelPlural": "Locations",
    "attributes": [
        {
            "key": "name",
            "label": "Location Name",
            "labelPlural": "Location Names",
            "visible": True,
            "required": True,
            "filterable": True,
            "mappings": None,
        },
        {
            "key": "primaryAssignedPerson",
            "label": "Primary Assigned Person",
            "labelPlural": "Primary Assigned Persons",
            "visible": False,
            "required": False,
            "filterable": True,
            "mappings": None,
        },
        {
            "key": "additionalAssignedPerson",
            "label": "Additional Assigned Person",
            "labelPlural": "Additional Assigned Persons",
            "visible": False,
            "required": False,
            "filterable": True,
            "mappings": None,
        },
        {
            "key": "externalKey",
            "label": "External Reference ID",
            "labelPlural": "External Reference IDs",
            "visible": False,
            "required": False,
            "filterable": False,
            "mappings": None,
        },
    ],
}


configure_tenant_mutation = """
        mutation configureTenant($tenantAttributes: EntityConfigurationInput!) {
            configureTenant(entityConfiguration: $tenantAttributes) {
                key
                label
                labelPlural
                defaultLabel
                defaultLabelPlural
                attributes {
                    key
                    label
                    labelPlural
                    defaultLabel
                    defaultLabelPlural
                    mandatory
                    required
                    visible
                    filterable
                    mappings
                }
            }
        }
    """


@pytest.mark.asyncio
@pytest.mark.integration
async def test_configure_tenant(
    execute_gql: ExecuteGQL, configurations_manager: ConfigurationsManager
) -> None:
    original_config = await configurations_manager.load(
        "APP.WORK_PACKAGE.ATTRIBUTES", None
    )
    assert original_config
    json_object = json.loads(original_config)
    attributes = json_object["attributes"]
    attribute_dict = dict()
    for attribute in attributes:
        attribute_dict[attribute.pop("key")] = attribute
    assert attribute_dict["name"]["label"] == "Work Package Name"
    payload = jsonable_encoder(work_package_config)

    response = await execute_gql(
        **{
            "operation_name": "configureTenant",
            "query": configure_tenant_mutation,
            "variables": {"tenantAttributes": payload},
        }
    )
    data = response["configureTenant"]
    attributes = data.get("attributes")
    for attribute in attributes:
        attribute_dict[attribute.pop("key")] = attribute
    assert attribute_dict["name"]["label"] == "The Work Unit Thingy"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_missing_required_fields_throws_exception(
    execute_gql: ExecuteGQL,
) -> None:
    payload = jsonable_encoder(missing_required_fields_config)

    response = await execute_gql(
        **{
            "operation_name": "configureTenant",
            "query": configure_tenant_mutation,
            "variables": {"tenantAttributes": payload},
        },
        raw=True
    )
    errors = response.json()["errors"]
    assert errors[0]["message"]

    assert all(
        name in errors[0]["message"]
        for name, attribute in ENTITY_SCHEMAS["workPackage"].attributes.items()
        if attribute.mandatory and name not in ("name", "externalKey")
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_mandatory_variables_must_be_visible(
    execute_gql: ExecuteGQL,
) -> None:
    payload = jsonable_encoder(mandatory_variables_not_visible)

    response = await execute_gql(
        **{
            "operation_name": "configureTenant",
            "query": configure_tenant_mutation,
            "variables": {"tenantAttributes": payload},
        },
        raw=True
    )
    configure_tenant_attributes = response.json()["data"]["configureTenant"][
        "attributes"
    ]

    for attribute in configure_tenant_attributes:
        if attribute.get("key") == "name":
            assert attribute.get("mandatory") and attribute.get("visible")

        if attribute.get("key") == "primaryAssignedPerson":
            assert not attribute.get("mandatory") and not attribute.get("visible")

        if attribute.get("key") == "additionalAssignedPerson":
            assert not attribute.get("mandatory")
            assert not attribute.get("visible")
