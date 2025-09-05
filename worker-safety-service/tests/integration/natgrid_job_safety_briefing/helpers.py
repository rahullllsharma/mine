import uuid
from datetime import datetime, timezone
from typing import Any

from tests.factories import LocationFactory, WorkPackageFactory
from tests.integration.conftest import ExecuteGQL
from worker_safety_service.models import (
    AsyncSession,
    Location,
    RiskLevel,
    User,
    WorkPackage,
)

save_natgrid_job_safety_briefing_mutation = {
    "operation_name": "saveNatgridJobSafetyBriefing",
    "query": """
        mutation saveNatgridJobSafetyBriefing($natgridJobSafetyBriefing: NatGridJobSafetyBriefingInput!, $formStatus: FormStatusInput!) {
            saveNatgridJobSafetyBriefing(natgridJobSafetyBriefing: $natgridJobSafetyBriefing, formStatus : $formStatus) {
                id
                status
                completedAt
                barnLocation {
                    id
                    name
                }
                contents {
                    completions {
                        completedAt
                    }
                    hazardsControl{
                        energyTypes
                    }
                    generalReferenceMaterials {
                        id
                        link
                        name
                        category
                    }
                    medicalInformation {
                        primaryFireSupressionLocation {
                            id
                            primaryFireSupressionLocationName
                        }
                        customPrimaryFireSupressionLocation {
                            address
                        }
                    }
                }
                createdBy {
                    id
                }
            }
        }
    """,
}

delete_natgrid_job_safety_briefing_mutation = {
    "operation_name": "DeleteNatGridJobSafetyBriefing",
    "query": """
        mutation DeleteNatGridJobSafetyBriefing($id: UUID!) {
            deleteNatgridJobSafetyBriefing(id: $id)
        }
    """,
}

reopen_natgrid_job_safety_briefing_mutation = {
    "operation_name": "ReopenNatGridJobSafetyBriefing",
    "query": """
        mutation ReopenNatGridJobSafetyBriefing($id: UUID!) {
            reopenNatgridJobSafetyBriefing(id: $id){
                id
                status
            }
        }
    """,
}
get_job_safety_briefing__by_id_query = {
    "operation_name": "GetNatGridJobSafetyBriefing",
    "query": """
        query GetNatGridJobSafetyBriefing($id: UUID!) {
            natgridJobSafetyBriefing(id: $id) {
                id
                contents {
                jsbMetadata {
                    briefingDateTime
                }
                taskHistoricIncidents{
                    id
                    name
                    historicIncidents
                }
                crewSignOff {
                    crewSign {
                        crewDetails {
                            id
                            name
                        }
                    }
                }
                energySourceControl {
                    energized
                    deEnergized
                    controls {
                        id
                        name
                    }
                    clearanceTypes {
                        id
                        clearanceTypes
                    }
                    pointsOfProtection {
                        id
                        name
                        details
                    }
                }
                jsbId
                groupDiscussion {
                    groupDiscussionNotes
                    viewed
                }
                gpsCoordinates {
                    latitude
                    longitude
                }
                workLocation {
                    address
                }
                workPackageMetadata {
                    workPackageLocationId
                }
                medicalInformation {
                    primaryFireSupressionLocation {
                        id
                        primaryFireSupressionLocationName
                    }
                    customPrimaryFireSupressionLocation {
                        address
                    }
                }
            }
          }
        }
    """,
}

get_recently_used_crew_leader = {
    "operation_name": "GetRecentlyUsedCrewLeader",
    "query": """
        query GetRecentlyUsedCrewLeader {
            recentlyUsedCrewLeaders {
                id
                name
            }
        }
    """,
}

get_last_natgrid_jsb_query = {
    "operation_name": "GetLastNatGridJobSafetyBriefing",
    "query": """
        query GetLastNatGridJobSafetyBriefing {
            lastNatgridJobSafetyBriefing {
                id
                createdBy {
                    id
                }
            }
        }
    """,
}


async def execute_save_natgrid_jsb(
    execute_gql: ExecuteGQL,
    data: dict,
    status: dict,
    raw: bool = False,
    user: User | None = None,
) -> Any:
    response = await execute_gql(
        **save_natgrid_job_safety_briefing_mutation,
        variables={"natgridJobSafetyBriefing": data, "formStatus": status},
        raw=raw,
        user=user,
    )
    if raw:
        return response
    else:
        return response["saveNatgridJobSafetyBriefing"]


async def execute_delete_natgrid_jsb(
    execute_gql: ExecuteGQL,
    jsb_id: uuid.UUID,
    raw: bool = False,
    user: User | None = None,
) -> Any:
    response = await execute_gql(
        **delete_natgrid_job_safety_briefing_mutation,
        variables={"id": str(jsb_id)},
        raw=raw,
        user=user,
    )

    if raw:
        return response
    else:
        return response["deleteNatgridJobSafetyBriefing"]


async def execute_reopen_natgrid_jsb(
    execute_gql: ExecuteGQL,
    jsb_id: uuid.UUID,
    raw: bool = False,
    user: User | None = None,
) -> Any:
    response = await execute_gql(
        **reopen_natgrid_job_safety_briefing_mutation,
        variables={"id": str(jsb_id)},
        raw=raw,
        user=user,
    )

    if raw:
        return response
    else:
        return response["reopenNatgridJobSafetyBriefing"]


async def build_natgrid_jsb_data(
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
    }
    return report_request, project, location


async def build_natgrid_jsb_data_without_date(
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


async def build_natgrid_jsb_data_with_critical_task_and_job_description(
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
        "criticalTasksSelections": {
            "taskSelections": [
                {
                    "id": uuid.uuid4(),
                    "riskLevel": RiskLevel.HIGH.name,
                    "fromWorkOrder": True,
                }
            ],
            "jobDescription": "test",
        },
    }
    return report_request, project, location


async def build_natgrid_jsb_with_multilocation_field(
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
        "workLocationWithVoltageInfo": [
            {
                "createdAt": datetime.now(),
                "address": "test",
                "landmark": "test",
                "city": "test",
                "state": "test",
                "gpsCoordinates": {
                    "latitude": 1.0,
                    "longitude": 1.0,
                },
                "circuit": "25",
                "voltageInformation": {
                    "voltage": {
                        "id": str(uuid.uuid4()),
                        "value": "NE 301 – 750",
                        "other": True,
                    },
                    "minimumApproachDistance": {
                        "phaseToGround": '13" (1\'-1")',
                        "phaseToPhase": '13" (1\'-1")',
                    },
                },
            },
            {
                "createdAt": datetime.now(),
                "address": "test2",
                "landmark": "test2",
                "city": "test2",
                "state": "test2",
                "gpsCoordinates": {
                    "latitude": 1.0,
                    "longitude": 1.0,
                },
                "circuit": "25",
                "voltageInformation": {
                    "voltage": {
                        "id": str(uuid.uuid4()),
                        "value": "NE 301 – 750",
                        "other": True,
                    },
                    "minimumApproachDistance": {
                        "phaseToGround": '13" (1\'-1")',
                        "phaseToPhase": None,
                    },
                },
            },
        ],
    }
    return report_request, project, location


async def build_natgrid_jsb_for_checking_backward_compatibility(
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
        "workLocation": {
            "address": "test",
            "landmark": "test",
            "city": "test",
            "state": "test",
            "vehicleNumber": ["25UUU"],
            "minimumApproachDistance": "26",
        },
        "gpsCoordinates": [
            {
                "latitude": 1.0,
                "longitude": 1.0,
            },
        ],
        "voltageInfo": {"circuit": "25", "voltages": "25"},
    }
    return report_request, project, location


async def build_natgrid_jsb_data_with_additional_comments_and_dig_safe(
    db_session: AsyncSession,
) -> tuple[dict, WorkPackage, Location]:
    additional_comments = "testing"
    dig_safe = "testingDigSafe"
    project: WorkPackage = await WorkPackageFactory.persist(db_session)
    location: Location = await LocationFactory.persist(
        db_session, project_id=project.id
    )
    report_request = {
        "workPackageMetadata": {
            "workPackageLocationId": str(location.id),
        },
        "siteConditions": {
            "siteConditionSelections": {
                "id": uuid.uuid4(),
                "recommended": True,
                "selected": True,
            },
            "additionalComments": additional_comments,
            "digSafe": dig_safe,
        },
    }
    return report_request, project, location


async def build_natgrid_jsb_data_with_historic_incidents(
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
        "taskHistoricIncidents": [
            {
                "id": uuid.uuid4(),
                "name": "testing",
                "historicIncidents": [f"{uuid.uuid4()}", f"{uuid.uuid4()}"],
            }
        ],
    }
    return report_request, project, location


async def build_natgrid_jsb_data_with_general_reference_materials(
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
        "generalReferenceMaterials": [
            {
                "id": 1,
                "name": "Commercial Driver License (CDL) Training Videos",
                "link": "https://nationalgridplc.sharepoint.com/sites/GRP-INT-USAcademyDocumentStore/AcadRes/SitePages/CDL.aspx",
                "category": None,
            },
            {
                "id": 2,
                "name": "Electric T&D Training Videos",
                "link": "https://nationalgridplc.sharepoint.com/sites/GRP-INT-USAcademyDocumentStore/AcadRes/SitePages/td_videos.aspx",
                "category": "Training Videos",
            },
        ],
    }
    return report_request, project, location


async def build_natgrid_jsb_data_with_barn_location(
    db_session: AsyncSession,
) -> tuple[dict, WorkPackage, Location]:
    project: WorkPackage = await WorkPackageFactory.persist(db_session)
    location: Location = await LocationFactory.persist(
        db_session, project_id=project.id
    )
    report_request = {
        "barnLocation": {
            "id": str(uuid.uuid4()),
            "name": "test Barn Location",
        }
    }
    return report_request, project, location


async def execute_get_natgrid_jsb_by_id(
    execute_gql: ExecuteGQL,
    natgrid_jsb_id: uuid.UUID,
    raw: bool = False,
    user: User | None = None,
) -> Any:
    response = await execute_gql(
        **get_job_safety_briefing__by_id_query,
        variables={"id": str(natgrid_jsb_id)},
        raw=raw,
        user=user,
    )
    if raw:
        return response
    else:
        return response["natgridJobSafetyBriefing"]


async def execute_get_recently_used_crew_leader(
    execute_gql: ExecuteGQL,
    raw: bool = False,
    user: User | None = None,
) -> Any:
    response = await execute_gql(
        **get_recently_used_crew_leader,
        raw=raw,
        user=user,
    )
    if raw:
        return response
    else:
        return response["recentlyUsedCrewLeaders"]


async def execute_get_last_natgrid_jsb(
    execute_gql: ExecuteGQL,
    raw: bool = False,
    user: User | None = None,
) -> Any:
    response = await execute_gql(
        **get_last_natgrid_jsb_query,
        raw=raw,
        user=user,
    )
    if raw:
        return response
    else:
        return response["lastNatgridJobSafetyBriefing"]
