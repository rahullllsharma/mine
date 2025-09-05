import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Union

from fastapi.encoders import jsonable_encoder

from tests.factories import (
    ContractorFactory,
    LocationFactory,
    ManagerUserFactory,
    SupervisorUserFactory,
    WorkPackageFactory,
    WorkTypeFactory,
)
from tests.integration.conftest import ExecuteGQL
from worker_safety_service.dal.configurations import (
    ENTITY_SCHEMAS,
    ConfigurationsManager,
)
from worker_safety_service.models import (
    Activity,
    AsyncSession,
    Location,
    SiteCondition,
    SiteConditionControl,
    SiteConditionHazard,
    Task,
    TaskControl,
    TaskHazard,
    WorkPackage,
)

################################################################################
# GQL Mutation helpers
################################################################################

create_project_mutation = {
    "operation_name": "CreateProject",
    "query": """
mutation CreateProject($project: CreateProjectInput!) {
  project: createProject(project: $project) {
    id name number
    manager { id name }
    supervisor { id name }
    additionalSupervisors { id name }
    contractor { id name }
    locations {
        id name latitude longitude
        supervisor { id name }
        additionalSupervisors { id name }
    }
  }
}
""",
}

edit_project_mutation = {
    "operation_name": "EditProject",
    "query": """
mutation EditProject($project: EditProjectInput!) {
  project: editProject(project: $project) {
    id name number
    manager { id name }
    supervisor { id name }
    additionalSupervisors { id name }
    contractor { id name }
    locations {
        id name latitude longitude
        supervisor { id name }
        additionalSupervisors { id name }
        externalKey
    }
  }
}
""",
}

###################################################################################
# gql_* helpers
###################################################################################
# Maybe there's a strawberry/pydantic way to make these conversions?
# Mostly it camelCases field names, stringifies dates, and handles some enum
# discrepancies.


def gql_project(project: Union[WorkPackage, dict[str, Any]]) -> dict[str, Any]:
    """
    Converts the passed model or dict to a gql-friendly project input.
    """
    proj = jsonable_encoder(project)
    ret = {
        "name": proj["name"],
        "number": proj.get("external_key"),
        "description": proj.get("description"),
        "libraryRegionId": str(proj["region_id"]) if proj.get("region_id") else None,
        "libraryDivisionId": (
            str(proj["division_id"]) if proj.get("division_id") else None
        ),
        "libraryProjectTypeId": (
            str(proj["work_type_id"]) if proj.get("work_type_id") else None
        ),
        "workTypeIds": (
            [str(i) for i in proj["work_type_ids"]]
            if proj.get("work_type_ids")
            else None
        ),
        "status": proj["status"].upper(),  # could be brittle
        "engineerName": proj.get("engineer_name"),
        "projectZipCode": proj.get("zip_code") or None,
        "contractReference": proj.get("contract_reference"),
        "contractName": proj.get("contract_name"),
        "libraryAssetTypeId": (
            str(proj["asset_type_id"]) if proj.get("asset_type_id") else None
        ),
        "startDate": str(proj["start_date"]),
        "endDate": str(proj["end_date"]),
        "managerId": str(proj["manager_id"]) if proj.get("manager_id") else None,
        "supervisorId": (
            str(proj["primary_assigned_user_id"])
            if proj.get("primary_assigned_user_id")
            else None
        ),
        "additionalSupervisors": (
            [str(i) for i in proj["additional_assigned_users_ids"]]
            if proj.get("additional_assigned_users_ids")
            else None
        ),
        "contractorId": (
            str(proj["contractor_id"]) if proj.get("contractor_id") else None
        ),
    }
    if "id" in proj:
        ret["id"] = str(proj["id"])
    return ret


def gql_location(location: Union[Location, dict[str, Any]]) -> dict[str, Any]:
    """
    Converts the passed model or dict to a gql-friendly location input.
    """
    loc = jsonable_encoder(location)
    ret = {
        "name": loc["name"],
        "latitude": loc["geom"]["latitude"],
        "longitude": loc["geom"]["longitude"],
        "supervisorId": str(loc["supervisor_id"]),
        "additionalSupervisors": loc.get("additional_supervisor_ids", []),
        "externalKey": loc.get("external_key", None),
    }
    if "id" in loc:
        ret["id"] = str(loc["id"])
    return ret


def gql_activity(activity: Union[Activity, dict[str, Any]]) -> dict[str, Any]:
    """
    Converts the passed model or dict to a gql-friendly activity input.
    """
    t = jsonable_encoder(activity)
    ret = {
        "status": t["status"].upper(),
    }
    if "id" in t:
        ret["id"] = str(t["id"])
    if "name" in t:
        ret["name"] = str(t["name"])
    if "start_date" in t:
        ret["startDate"] = str(t["start_date"])
    if "end_date" in t:
        ret["endDate"] = str(t["end_date"])
    if "location_id" in t:
        ret["locationId"] = str(t["location_id"])
    crew_id = t.get("crew_id")
    if crew_id:
        ret["crewId"] = str(crew_id)
    library_activity_type_id = t.get("library_activity_type_id")
    if library_activity_type_id:
        ret["libraryActivityTypeId"] = str(library_activity_type_id)
    return ret


def gql_task(task: Union[Task, dict[str, Any]]) -> dict[str, Any]:
    """
    Converts the passed model or dict to a gql-friendly task input.
    """
    t = jsonable_encoder(task)
    ret = {}
    if "id" in t:
        ret["id"] = str(t["id"])
    return ret


def gql_site_condition(
    site_condition: Union[SiteCondition, dict[str, Any]]
) -> dict[str, Any]:
    """
    Converts the passed model or dict to a gql-friendly site_condition input.
    """
    t = jsonable_encoder(site_condition)
    ret: dict[str, Any] = {
        "hazards": [],
    }
    if "id" in t:
        ret["id"] = str(t["id"])
    return ret


def gql_hazard(
    hazard: Union[SiteConditionHazard, TaskHazard, dict[str, Any]]
) -> dict[str, Any]:
    """
    Converts the passed model or dict to a gql-friendly hazard input.
    """
    h = jsonable_encoder(hazard)
    ret = {
        "isApplicable": h["is_applicable"],
        "libraryHazardId": h["library_hazard_id"] if "library_hazard_id" in h else None,
    }
    if "id" in h:
        ret["id"] = str(h["id"])
    return ret


def gql_control(
    control: Union[
        SiteConditionControl,
        TaskControl,
        dict[str, Any],
    ]
) -> dict[str, Any]:
    """
    Converts the passed model or dict to a gql-friendly control input.
    """
    c = jsonable_encoder(control)
    ret = {
        "isApplicable": c["is_applicable"],
        "libraryControlId": (
            c["library_control_id"] if "library_control_id" in c else None
        ),
    }
    if "id" in c:
        ret["id"] = str(c["id"])
    return ret


################################################################################
# GraphQL mutation helpers
################################################################################


async def valid_project_request(
    db_session: AsyncSession,
    locations_length: int = 1,
    persist: bool = False,
) -> dict:
    manager_id = (await ManagerUserFactory.persist(db_session)).id
    supervisor_id = (await SupervisorUserFactory.persist(db_session)).id
    supervisor_2_id = (await SupervisorUserFactory.persist(db_session)).id
    contractor_id = (await ContractorFactory.persist(db_session)).id

    work_type_id = (await WorkTypeFactory.persist(db_session)).id

    project_kwargs = {
        "manager_id": manager_id,
        "primary_assigned_user_id": supervisor_id,
        "additional_assigned_users_ids": [supervisor_2_id],
        "contractor_id": contractor_id,
        "work_type_ids": [work_type_id],
    }

    project: WorkPackage
    project_id: uuid.UUID | None = None
    if persist:
        project = await WorkPackageFactory.persist(db_session, **project_kwargs)
        project_id = project.id
    else:
        project = WorkPackageFactory.build(**project_kwargs)  # type: ignore
        await WorkPackageFactory.db_deps(db_session, project)

    project_data = gql_project(project.dict(exclude={} if persist else {"id"}))
    project_data["locations"] = [
        await valid_project_location_request(
            db_session, project_id=project_id, persist=persist
        )
        for i in range(locations_length)
    ]
    return project_data


async def valid_project_location_request(
    db_session: AsyncSession,
    project_id: uuid.UUID | str | None = None,
    persist: bool = False,
) -> dict:
    supervisor_id = (await SupervisorUserFactory.persist(db_session)).id
    supervisor_2_id = (await SupervisorUserFactory.persist(db_session)).id
    location_kwargs = {
        "supervisor_id": supervisor_id,
        "additional_supervisor_ids": [supervisor_2_id],
    }
    if project_id:
        location_kwargs["project_id"] = project_id

    location: Location
    if persist:
        location = await LocationFactory.persist(db_session, **location_kwargs)
    else:
        location = LocationFactory.build(**location_kwargs)  # type: ignore
    return gql_location(location.dict(exclude={} if persist else {"id"}))


async def create_project_gql(
    execute_gql: ExecuteGQL, project_data: dict, with_errors: bool = False
) -> dict:
    response = await execute_gql(
        **create_project_mutation, variables={"project": project_data}, raw=with_errors
    )
    if with_errors:
        data: dict = response.json()
        return data
    else:
        project: dict = response["project"]
        return project


async def create_project(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    locations_length: int = 1,
    populate_ids: bool = False,
) -> tuple[dict, dict]:
    project_data = await valid_project_request(
        db_session, locations_length=locations_length
    )
    data = await create_project_gql(execute_gql, project_data)
    assert len(data["locations"]) == locations_length

    for p_loc, d_loc in zip(project_data["locations"], data["locations"]):
        d_loc["externalKey"] = p_loc.get("externalKey", None)

    if populate_ids:
        project_data["id"] = data["id"]
        # match response using supervisor
        locations_by_supervisor = {
            i["supervisorId"]: i for i in project_data["locations"]
        }
        for location in data["locations"]:
            locations_by_supervisor[location["supervisor"]["id"]]["id"] = location["id"]

    return project_data, data


async def edit_project_gql(
    execute_gql: ExecuteGQL, project_data: dict, with_errors: bool = False
) -> dict:
    response = await execute_gql(
        **edit_project_mutation, variables={"project": project_data}, raw=with_errors
    )
    if with_errors:
        data: dict = response.json()
        return data
    else:
        project: dict = response["project"]
        return project


################################################################################
# Assert Helpers
################################################################################


def assert_recent_datetime(t: datetime | None, **kwargs: Any) -> None:
    """
    Asserts the passed datetime occurred in the last minute. Passes the **kwargs
    to `timedelta` if that you want a longer time range.

    If the `t` has timezone info, this will branch to compare to tz-aware datetimes.
    """
    assert t
    assert t.tzinfo
    assert t > (datetime.now(timezone.utc) - timedelta(minutes=1, **kwargs))
    assert t < datetime.now(timezone.utc)


async def update_configuration(
    configurations_manager: ConfigurationsManager,
    tenant_id: uuid.UUID,
    section_name: str,
    required_fields: list[str] | None,
) -> None:
    configs = await configurations_manager.get_entities_with_defaults(
        tenant_id, [section_name]
    )
    tenant_configs, _ = configs[section_name]

    for attribute in tenant_configs.attributes or []:
        schema_attribute = ENTITY_SCHEMAS[section_name].attributes[attribute.key]
        if not schema_attribute.mandatory and schema_attribute.model_attribute:
            attribute.visible = True
            attribute.required = bool(
                required_fields is None
                or schema_attribute.model_attribute in required_fields
            )

    await configurations_manager.update_section(tenant_configs, tenant_id)
