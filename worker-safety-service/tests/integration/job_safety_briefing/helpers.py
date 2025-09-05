import uuid
from datetime import datetime, timezone
from typing import Any

from faker import Faker

from tests.factories import (
    JobSafetyBriefingFactory,
    LocationFactory,
    WorkPackageFactory,
)
from tests.integration.conftest import ExecuteGQL
from worker_safety_service.models import AsyncSession, Location, User, WorkPackage
from worker_safety_service.models.forms import JobSafetyBriefing

fake = Faker()

get_job_safety_briefing__by_id_query = {
    "operation_name": "GetJobSafetyBriefing",
    "query": """
        query GetJobSafetyBriefing($id: UUID!) {
            jobSafetyBriefing(id: $id) {
              id
              contents {
                completions {
                    completedBy {
                        id
                        name
                    }
                    completedAt
                }
                controlAssessmentSelections {
                    hazardId
                    controlIds
                    controlSelections {
                        id
                        recommended
                        selected
                    }
                }
                emergencyContacts {
                  name
                  phoneNumber
                  primary
                }
                jsbId
                jsbMetadata {
                  briefingDateTime
                }
                nearestMedicalFacility {
                  description
                }
                taskSelections {
                  id
                  riskLevel
                  fromWorkOrder
                }
                activities {
                  name
                  tasks {
                    fromWorkOrder
                    riskLevel
                    id
                  }
                }
                workLocation {
                  address
                  city
                  description
                  state
                  operatingHq
                }
                workProcedureSelections {
                  id
                  values
                }
                otherWorkProcedures
                energySourceControl {
                  arcFlashCategory
                  clearancePoints
                  ewp {
                    id
                    metadata {
                      completed
                      issued
                      issuedBy
                      procedure
                      receivedBy
                      remote
                    }
                    equipmentInformation {
                      circuitBreaker
                      switch
                      transformer
                    }
                    referencePoints
                  }
                  transferOfControl
                  voltages {
                    type
                    unit
                    value
                  }
                }
                siteConditionSelections {
                  id
                  recommended
                  selected
                }
                crewSignOff {
                    name
                    signature {
                        displayName
                        name
                    }
                }
                photos {
                    date
                    displayName
                    name
                    size
                    time
                    url
                }
                groupDiscussion {
                    viewed
                }
                documents {
                    name
                    displayName
                }
              }
            }
          }
    """,
}

save_job_safety_briefing_mutation = {
    "operation_name": "SaveJobSafetyBriefing",
    "query": """
        mutation SaveJobSafetyBriefing($jobSafetyBriefingInput: SaveJobSafetyBriefingInput!) {
            saveJobSafetyBriefing(jobSafetyBriefingInput: $jobSafetyBriefingInput) {
                id
                status
                completedAt
                completedBy {
                    id
                    name
                }
                contents {
                    controlAssessmentSelections {
                        hazardId
                        controlIds
                        controlSelections {
                            id
                            recommended
                            selected
                        }
                    }
                    emergencyContacts {
                        name
                        phoneNumber
                        primary
                    }
                    jsbId
                    jsbMetadata {
                        briefingDateTime
                    }
                    sourceInfo {
                        appVersion
                        sourceInformation
                    }
                    gpsCoordinates
                    {
                        latitude
                        longitude
                    }
                    nearestMedicalFacility {
                        description
                    }
                    customNearestMedicalFacility{
                        address
                    }
                    taskSelections {
                        id
                        name
                        riskLevel
                        fromWorkOrder
                    }
                    activities {
                        name
                        tasks {
                            fromWorkOrder
                            riskLevel
                            id
                        }
                    }
                    workLocation {
                        address
                        city
                        description
                        state
                        operatingHq
                    }
                    workProcedureSelections {
                        id
                        values
                    }
                    otherWorkProcedures
                    energySourceControl {
                        arcFlashCategory
                        clearancePoints
                        ewp {
                        id
                        metadata {
                            completed
                            issued
                            issuedBy
                            procedure
                            receivedBy
                            remote
                        }
                        equipmentInformation {
                            circuitBreaker
                            switch
                            transformer
                        }
                        referencePoints
                        }
                        transferOfControl
                        voltages {
                        type
                        unit
                        value
                        }
                    }
                    siteConditionSelections {
                        id
                        recommended
                        selected
                    }
                    crewSignOff {
                        name
                        signature {
                            displayName
                            name
                        }
                    }
                    photos {
                        date
                        displayName
                        name
                        size
                        time
                        url
                    }
                    groupDiscussion {
                        viewed
                    }
                    documents {
                        name
                        displayName
                    }
                }
            }
        }
    """,
}

get_job_safety_briefings_for_project_location_query = {
    "operation_name": "GetJobSafetyBriefingsForProjectLocation",
    "query": """
         query GetJobSafetyBriefingsForProjectLocation($id: UUID) {
           projectLocations(id: $id) {
             id
             name
             jobSafetyBriefings {
               id
               name
               status
               completedAt
               completedBy {
                 id
                 name
               }
             }
           }
         }

    """,
}

delete_job_safety_briefing_mutation = {
    "operation_name": "DeleteJobSafetyBriefing",
    "query": """
        mutation DeleteJobSafetyBriefing($id: UUID!) {
            deleteJobSafetyBriefing(id: $id)
        }
    """,
}

complete_job_safety_briefing_mutation = {
    "operation_name": "CompleteJobSafetyBriefing",
    "query": """
        mutation CompleteJobSafetyBriefing($jobSafetyBriefingInput: SaveJobSafetyBriefingInput!) {
            completeJobSafetyBriefing(jobSafetyBriefingInput: $jobSafetyBriefingInput) {
                id
                status
                completedAt
                completedBy {
                    id
                    name
                }
                contents {
                    completions {
                        completedBy {
                            id
                            name
                        }
                        completedAt
                    }
                }
            }
        }
    """,
}

get_last_added_job_safety_briefing_query = {
    "operation_name": "GetLastAddedJobSafetyBriefing",
    "query": """
        query GetLastAddedJobSafetyBriefing($filterOn: JSBFiltersOnEnum!, $projectLocationId: UUID) {
            lastAddedJobSafetyBriefing(
                filterOn: $filterOn
                projectLocationId: $projectLocationId
            ) {
                id
                name
                status
                completedAt
                createdBy {
                    firstName
                    id
                    lastName
                    name
                }
                completedBy {
                    firstName
                    id
                    lastName
                    name
                }
                location {
                    id
                    latitude
                    longitude
                }
                contents {
                    nearestMedicalFacility {
                        address
                        city
                        description
                        distanceFromJob
                        phoneNumber
                        state
                        zip
                    }
                    emergencyContacts {
                        name
                        phoneNumber
                        primary
                    }
                    aedInformation {
                        location
                    }
                    workLocation {
                        address
                        city
                        description
                        state
                        operatingHq
                    }
                }
            }
        }
    """,
}

reopen_job_safety_briefing_mutation = {
    "operation_name": "ReopenJobSafetyBriefing",
    "query": """
        mutation ReopenJobSafetyBriefing($id: UUID!) {
            reopenJobSafetyBriefing(id: $id) {
                id
                status
                completedAt
                completedBy {
                    id
                    name
                }
            }
        }
    """,
}

update_other_nearest_medical_facility_jsb_mutation = {
    "operation_name": "SaveJobSafetyBriefing",
    "query": """
        mutation SaveJobSafetyBriefing($jobSafetyBriefingInput: SaveJobSafetyBriefingInput!) {
            saveJobSafetyBriefing(jobSafetyBriefingInput: $jobSafetyBriefingInput) {
                id
                contents {
                    nearestMedicalFacility {
                        description
                    }
                    customNearestMedicalFacility{
                        address
                    }
                }
            }
        }
    """,
}

get_last_added_adhoc_job_safety_briefing_query = {
    "operation_name": "GetLastAddedAdhocJobSafetyBriefing",
    "query": """
        query GetLastAddedAdhocJobSafetyBriefing{
            lastAddedAdhocJobSafetyBriefing{
                id
                name
                status
                completedAt
                createdBy {
                    firstName
                    id
                    lastName
                    name
                }
                completedBy {
                    firstName
                    id
                    lastName
                    name
                }
                location {
                    id
                    latitude
                    longitude
                }
                contents {
                    nearestMedicalFacility {
                        address
                        city
                        description
                        distanceFromJob
                        phoneNumber
                        state
                        zip
                    }
                    emergencyContacts {
                        name
                        phoneNumber
                        primary
                    }
                    aedInformation {
                        location
                    }
                    workLocation {
                        address
                        city
                        description
                        state
                        operatingHq
                    }
                }
            }
        }
    """,
}


async def execute_get_jsb_by_id(
    execute_gql: ExecuteGQL,
    jsb_id: uuid.UUID,
    raw: bool = False,
    user: User | None = None,
) -> Any:
    response = await execute_gql(
        **get_job_safety_briefing__by_id_query,
        variables={"id": str(jsb_id)},
        raw=raw,
        user=user,
    )
    if raw:
        return response
    else:
        return response["jobSafetyBriefing"]


async def execute_save_jsb(
    execute_gql: ExecuteGQL, data: dict, raw: bool = False, user: User | None = None
) -> Any:
    response = await execute_gql(
        **save_job_safety_briefing_mutation,
        variables={"jobSafetyBriefingInput": data},
        raw=raw,
        user=user,
    )
    if raw:
        return response
    else:
        return response["saveJobSafetyBriefing"]


async def execute_get_jsb_for_project_location(
    execute_gql: ExecuteGQL,
    project_location_id: uuid.UUID,
    raw: bool = False,
    user: User | None = None,
) -> Any:
    response = await execute_gql(
        **get_job_safety_briefings_for_project_location_query,
        variables={"id": str(project_location_id)},
        raw=raw,
        user=user,
    )
    if raw:
        return response
    else:
        return response["projectLocations"][0]


async def execute_delete_jsb(
    execute_gql: ExecuteGQL,
    jsb_id: uuid.UUID,
    raw: bool = False,
    user: User | None = None,
) -> Any:
    response = await execute_gql(
        **delete_job_safety_briefing_mutation,
        variables={"id": str(jsb_id)},
        raw=raw,
        user=user,
    )

    if raw:
        return response
    else:
        return response["deleteJobSafetyBriefing"]


async def execute_complete_jsb(
    execute_gql: ExecuteGQL,
    data: dict,
    raw: bool = False,
    user: User | None = None,
) -> Any:
    response = await execute_gql(
        **complete_job_safety_briefing_mutation,
        variables={"jobSafetyBriefingInput": data},
        raw=raw,
        user=user,
    )

    if raw:
        return response
    else:
        return response["completeJobSafetyBriefing"]


async def execute_last_added_jsb(
    execute_gql: ExecuteGQL,
    req: dict,
    raw: bool = False,
    user: User | None = None,
) -> Any:
    response = await execute_gql(
        **get_last_added_job_safety_briefing_query,
        variables={
            "filterOn": req["filterOn"],
            "projectLocationId": req["projectLocationId"],
        },
        raw=raw,
        user=user,
    )

    if raw:
        return response
    else:
        return response["lastAddedJobSafetyBriefing"]


async def execute_last_added_adhoc_jsb(
    execute_gql: ExecuteGQL,
    req: dict,
    raw: bool = False,
    user: User | None = None,
) -> Any:
    response = await execute_gql(
        **get_last_added_adhoc_job_safety_briefing_query,
        variables={},
        raw=raw,
        user=user,
    )

    if raw:
        return response
    else:
        return response["lastAddedAdhocJobSafetyBriefing"]


async def execute_reopen_jsb(
    execute_gql: ExecuteGQL,
    jsb_id: uuid.UUID,
    raw: bool = False,
    user: User | None = None,
) -> Any:
    response = await execute_gql(
        **reopen_job_safety_briefing_mutation,
        variables={"id": str(jsb_id)},
        raw=raw,
        user=user,
    )

    if raw:
        return response
    else:
        return response["reopenJobSafetyBriefing"]


async def build_jsb_data(
    db_session: AsyncSession, date: datetime | None = None
) -> tuple[dict, WorkPackage, Location]:
    project: WorkPackage = await WorkPackageFactory.persist(db_session)
    location: Location = await LocationFactory.persist(
        db_session, project_id=project.id
    )

    date = date or datetime.now(timezone.utc)
    report_request = {
        "jsbMetadata": {
            "briefingDateTime": str(date),
        },
        "workPackageMetadata": {
            "workPackageLocationId": str(location.id),
        },
        "sourceInfo": {
            "appVersion": "V1.1.1",
            "sourceInformation": "WEB_PORTAL",
        },
    }
    return report_request, project, location


async def build_jsb_data_with_crew_info(
    db_session: AsyncSession, date: datetime | None = None
) -> dict:
    project: WorkPackage = await WorkPackageFactory.persist(db_session)
    location: Location = await LocationFactory.persist(
        db_session, project_id=project.id
    )
    jsb: JobSafetyBriefing = await JobSafetyBriefingFactory.persist(db_session)
    crew_info = [
        {
            "managerId": str(uuid.uuid4()),
            "managerName": fake.name(),
            "managerEmail": fake.email(),
        },
        {
            "managerId": str(uuid.uuid4()),
            "managerName": fake.name(),
            "managerEmail": fake.email(),
        },
    ]
    date = date or datetime.now(timezone.utc)
    report_request = {
        "jsbId": jsb.id,
        "jsbMetadata": {
            "briefingDateTime": str(date),
        },
        "workPackageMetadata": {
            "workPackageLocationId": str(location.id),
        },
        "sourceInfo": {
            "appVersion": "V1.1.1",
            "sourceInformation": "WEB_PORTAL",
        },
        "crewSignOff": crew_info,
    }
    return report_request


async def build_jsb_data_without_date(
    db_session: AsyncSession,
) -> tuple[dict, WorkPackage, Location]:
    project: WorkPackage = await WorkPackageFactory.persist(db_session)
    location: Location = await LocationFactory.persist(
        db_session, project_id=project.id
    )

    report_request = {
        "workPackageMetadata": {
            "workPackageLocationId": str(location.id),
        },
    }
    return report_request, project, location
