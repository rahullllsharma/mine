import uuid
from typing import Any

from tests.factories import (
    ActivityFactory,
    LibraryControlFactory,
    TaskFactory,
    UserFactory,
)
from tests.integration.conftest import ExecuteGQL
from worker_safety_service import models
from worker_safety_service.models import AsyncSession, User

get_energy_based_observation_by_id_query = {
    "operation_name": "GetEnergyBasedObservation",
    "query": """ query GetEnergyBasedObservation($id: UUID!) {
        energyBasedObservation(id: $id) {
              completedAt
              createdAt
              id
              createdBy {
                firstName
                id
                lastName
                name
              }
              status
              contents {
                completions {
                  completedBy {
                    id
                    name
                  }
                  completedAt
                }
                activities {
                  id
                  name
                  tasks {
                    instanceId
                    fromWorkOrder
                    riskLevel
                    id
                    name
                    hazards {
                      directControlsImplemented
                      indirectControls
                      {
                        id
                        name
                      }
                      id
                      name
                      observed
                      reason
                    }
                  }
                }
                additionalInformation
                historicIncidents
                details {
                  departmentObserved {
                    id
                    name
                  }
                  workLocation
                  workOrderNumber
                  workType {
                    id
                    name
                  }
                  observationDate
                  observationTime
                  opcoObserved {
                    id
                    name
                  }
                  subopcoObserved {
                    id
                    name
                  }
                }
                gpsCoordinates {
                  latitude
                  longitude
                }
                highEnergyTasks {
                  instanceId
                  id
                  hazards {
                    directControlsImplemented
                    indirectControls
                    {
                        id
                        name
                    }
                    id
                    name
                    observed
                    reason
                  }
                  activityId
                  activityName
                }
                personnel {
                  id
                  name
                  role
                }
                photos {
                  category
                  crc32c
                  date
                  displayName
                  exists
                  id
                  md5
                  mimetype
                  name
                  signedUrl
                  size
                  time
                  url
                }
              }
            }
          }
        """,
}


save_energy_based_observation_mutation = {
    "operation_name": "SaveEnergyBasedObservation",
    "query": """mutation SaveEnergyBasedObservation($energyBasedObservationInput: EnergyBasedObservationInput!) {
            saveEnergyBasedObservation(energyBasedObservationInput: $energyBasedObservationInput) {
              completedAt
              id
              status
              createdBy {
                id
                lastName
                name
                firstName
              }
              createdAt
              contents {
                additionalInformation
                activities {
                  id
                  name
                  tasks {
                    instanceId
                    fromWorkOrder
                    id
                    name
                    riskLevel
                    hazards {
                      directControlsImplemented
                      indirectControls
                      {
                        id
                        name
                      }
                      id
                      name
                      observed
                      reason
                    }
                  }
                }
                details {
                  departmentObserved {
                    id
                    name
                  }
                  workLocation
                  workOrderNumber
                  workType {
                    id
                    name
                  }
                  observationDate
                  observationTime
                  opcoObserved {
                    id
                    name
                  }
                  subopcoObserved {
                    id
                    name
                  }
                }
                sourceInfo {
                  appVersion
                  sourceInformation
                }
                gpsCoordinates {
                  latitude
                  longitude
                }
                highEnergyTasks {
                  instanceId
                  id
                  hazards {
                    directControlsImplemented
                    id
                    name
                    indirectControls
                    {
                        id
                        name
                    }
                    observed
                    reason
                  }
                  activityId
                  activityName
                }
                historicIncidents
                personnel {
                  id
                  name
                  role
                }
                photos {
                  category
                  crc32c
                  date
                  displayName
                  exists
                  id
                  md5
                  mimetype
                  name
                  signedUrl
                  size
                  time
                  url
                }
              }
              completedBy {
                firstName
                id
                lastName
                name
              }
            }
          }
    """,
}

update_energy_based_observation_mutation = {
    "operation_name": "SaveEnergyBasedObservation",
    "query": """mutation SaveEnergyBasedObservation($energyBasedObservationInput: EnergyBasedObservationInput!, $id: UUID!) {
            saveEnergyBasedObservation(energyBasedObservationInput: $energyBasedObservationInput, id: $id) {
              completedAt
              id
              status
              createdBy {
                id
                lastName
                name
                firstName
              }
              createdAt
              contents {
                additionalInformation
                activities {
                  id
                  name
                  tasks {
                    instanceId
                    hazards {
                      directControlsImplemented
                      indirectControls
                      {
                        id
                        name
                      }
                      id
                      name
                      observed
                      reason
                    }
                    fromWorkOrder
                    id
                    name
                    riskLevel
                  }
                }
                details {
                  departmentObserved {
                    id
                    name
                  }
                  workLocation
                  workOrderNumber
                  workType {
                    id
                    name
                  }
                  observationDate
                  observationTime
                  opcoObserved {
                    id
                    name
                  }
                  subopcoObserved {
                    id
                    name
                  }
                }
                gpsCoordinates {
                  latitude
                  longitude
                }
                highEnergyTasks {
                  instanceId
                  id
                  hazards {
                    directControlsImplemented
                    id
                    name
                    indirectControls
                    {
                        id
                        name
                    }
                    observed
                    reason
                  }
                  activityId
                  activityName
                }
                historicIncidents
                personnel {
                  id
                  name
                  role
                }
                photos {
                  category
                  crc32c
                  date
                  displayName
                  exists
                  id
                  md5
                  mimetype
                  name
                  signedUrl
                  size
                  time
                  url
                }
              }
              completedBy {
                firstName
                id
                lastName
                name
              }
            }
          }
    """,
}

complete_energy_based_observation_mutation = {
    "operation_name": "CompleteEnergyBasedObservation",
    "query": """mutation  CompleteEnergyBasedObservation($id: UUID!, $energyBasedObservationInput: EnergyBasedObservationInput!) {
              completeEnergyBasedObservation(
                id: $id,
                energyBasedObservationInput: $energyBasedObservationInput
              ) {
              completedAt
              id
              status
              createdBy {
                id
                lastName
                name
                firstName
              }
              createdAt
              contents {
                additionalInformation
                activities {
                  id
                  name
                  tasks {
                    instanceId
                    hazards {
                      directControlsImplemented
                      indirectControls
                      {
                        id
                        name
                      }
                      id
                      name
                      observed
                      reason
                    }
                    fromWorkOrder
                    id
                    riskLevel
                  }
                }
                details {
                  departmentObserved {
                    id
                    name
                  }
                  workLocation
                  workOrderNumber
                  workType {
                    id
                    name
                  }
                  observationDate
                  observationTime
                  opcoObserved {
                    id
                    name
                  }
                  subopcoObserved {
                    id
                    name
                  }
                }
                gpsCoordinates {
                  latitude
                  longitude
                }
                highEnergyTasks {
                  instanceId
                  id
                  hazards {
                    directControlsImplemented
                    id
                    name
                    indirectControls
                    {
                        id
                        name
                    }
                    observed
                    reason
                    hecaScoreHazard
                    hecaScoreHazardPercentage
                  }
                  activityId
                  activityName
                  hecaScoreTask
                  hecaScoreTaskPercentage
                }
                historicIncidents
                personnel {
                  id
                  name
                  role
                }
                photos {
                  category
                  crc32c
                  date
                  displayName
                  exists
                  id
                  md5
                  mimetype
                  name
                  signedUrl
                  size
                  time
                  url
                }
              }
              completedBy {
                firstName
                id
                lastName
                name
              }
            }
          }
    """,
}

delete_energy_based_observation_mutation = {
    "operation_name": "deleteEnergyBasedObservation",
    "query": """
        mutation deleteEnergyBasedObservation($id: UUID!) {
          deleteEnergyBasedObservation(id: $id)
        }
    """,
}

reopen_energy_based_observation_mutation = {
    "operation_name": "ReopenEnergyBasedObservation",
    "query": """
         mutation ReopenEnergyBasedObservation($id: UUID!) {
             reopenEnergyBasedObservation(id: $id) {
                 id
                 status
                 completedAt
                 createdBy {
                   firstName
                   id
                   lastName
                   name
                 }
                 completedBy {
                     id
                     name
                 }
             }
         }
     """,
}


async def execute_get_ebo_by_id(
    execute_gql: ExecuteGQL,
    ebo_id: uuid.UUID,
    raw: bool = False,
    user: User | None = None,
) -> Any:
    response = await execute_gql(
        **get_energy_based_observation_by_id_query,
        variables={"id": str(ebo_id)},
        raw=raw,
        user=user,
    )

    if raw:
        return response
    else:
        return response["energyBasedObservation"]


async def execute_save_ebo(
    execute_gql: ExecuteGQL, data: dict, raw: bool = False, user: User | None = None
) -> Any:
    response = await execute_gql(
        **save_energy_based_observation_mutation,
        variables={"energyBasedObservationInput": data},
        raw=raw,
        user=user,
    )
    if raw:
        return response
    else:
        return response["saveEnergyBasedObservation"]


async def execute_update_ebo(
    execute_gql: ExecuteGQL, data: dict, raw: bool = False, user: User | None = None
) -> Any:
    response = await execute_gql(
        **update_energy_based_observation_mutation,
        variables=data,
        raw=raw,
        user=user,
    )
    return response if raw else response["saveEnergyBasedObservation"]


async def execute_complete_ebo(
    execute_gql: ExecuteGQL, data: dict, raw: bool = False, user: User | None = None
) -> Any:
    response = await execute_gql(
        **complete_energy_based_observation_mutation,
        variables=data,
        raw=raw,
        user=user,
    )
    return response if raw else response["completeEnergyBasedObservation"]


async def execute_delete_ebo(
    execute_gql: ExecuteGQL,
    ebo_id: uuid.UUID,
    raw: bool = False,
    user: User | None = None,
) -> Any:
    response = await execute_gql(
        **delete_energy_based_observation_mutation,
        variables={"id": str(ebo_id)},
        raw=raw,
        user=user,
    )

    return response if raw else response["deleteEnergyBasedObservation"]


async def execute_reopen_ebo(
    execute_gql: ExecuteGQL,
    ebo_id: uuid.UUID,
    raw: bool = False,
    user: User | None = None,
) -> Any:
    response = await execute_gql(
        **reopen_energy_based_observation_mutation,
        variables={"id": str(ebo_id)},
        raw=raw,
        user=user,
    )

    if raw:
        return response
    else:
        return response["reopenEnergyBasedObservation"]


async def build_ebo_data(
    db_session: AsyncSession,
) -> dict[Any, Any]:
    user: models.User = await UserFactory.persist(db_session)
    activity: models.Activity = await ActivityFactory.persist(db_session)
    task: models.Task = await TaskFactory.persist(db_session)

    report_request = {
        "details": {
            "observationDate": "2024-05-21",
            "observationTime": "21:06:00.000",
            "workOrderNumber": "",
            "workType": [
                {
                    "id": "5f12b55b-710f-4613-92f6-48bf0448c025",
                    "name": "Gas Transmission Construction",
                }
            ],
            "workLocation": "dasda",
            "departmentObserved": {
                "id": "453459ca-f72a-4271-9391-fd4bb0ee97f2",
                "name": "Operations geologist",
            },
            "opcoObserved": {
                "id": "a72271ef-5be2-4d3f-a93c-f21c3dfb73af",
                "name": "ComEd",
                "fullName": "ComEd",
            },
        },
        "additionalInformation": "Save EBO Data",
        "activities": {
            "id": activity.id,
            "name": activity.name,
            "tasks": {
                "id": task.id,
                "name": "test_task",
                "riskLevel": "HIGH",
                "fromWorkOrder": False,
            },
        },
        "personnel": {
            "name": f"{user.first_name} {user.last_name}",
            "id": user.id,
            "role": user.role,
        },
        "sourceInfo": {
            "appVersion": "V2.0.0",
            "sourceInformation": "WEB_PORTAL",
        },
    }

    return report_request


async def build_custom_ebo_data(
    db_session: AsyncSession, direct_controls_implemented: bool = True
) -> dict[Any, Any]:
    user: models.User = await UserFactory.persist(db_session)
    activity: models.Activity = await ActivityFactory.persist(db_session)
    task: models.Task = await TaskFactory.persist(db_session, name="test_task")
    control: models.LibraryControl = await LibraryControlFactory.persist(
        db_session, name="test_control"
    )

    report_request = {
        "additionalInformation": "Save EBO Data",
        "activities": {
            "id": activity.id,
            "name": activity.name,
            "tasks": {
                "id": task.id,
                "name": "test_task",
                "riskLevel": "HIGH",
                "fromWorkOrder": False,
            },
        },
        "personnel": {
            "name": f"{user.first_name} {user.last_name}",
            "id": user.id,
            "role": user.role,
        },
        "highEnergyTasks": {
            "id": uuid.uuid4(),
            "hazards": {
                "id": uuid.uuid4(),
                "name": "test_hazard_1",
                "reason": "spmething",
                "observed": True,
                "indirectControls": [{"id": control.id, "name": control.name}],
                "directControlsImplemented": direct_controls_implemented,
            },
        },
    }

    return report_request
