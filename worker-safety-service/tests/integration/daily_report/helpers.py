import datetime
import uuid
from typing import Any, Optional

from tests.factories import DailyReportFactory, LocationFactory, WorkPackageFactory
from tests.integration.conftest import ExecuteGQL
from worker_safety_service.config import settings
from worker_safety_service.graphql.types import FormStatus
from worker_safety_service.models import (
    AsyncSession,
    DailyReport,
    Location,
    User,
    WorkPackage,
)

get_daily_report_query = {
    "operation_name": "dailyReport",
    "query": """
  query dailyReport($id: UUID!, $status: FormStatus) {
    dailyReport(id: $id, status: $status) {
      id
      status
      completedBy {
        id
        name
      }
      completedAt
      sections {
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

get_daily_report_list_query = {
    "operation_name": "dailyReports",
    "query": """
  query dailyReports($projectLocationId: UUID!, $date: Date!) {
    dailyReports(projectLocationId: $projectLocationId, date: $date) {
      id
      status
      completedBy {
        id
        name
      }
      completedAt
      sections {
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

save_daily_report_mutation = {
    "operation_name": "SaveDailyReport",
    "query": """
mutation SaveDailyReport($dailyReportInput: SaveDailyReportInput!) {
  saveDailyReport(dailyReportInput: $dailyReportInput) {
    id status date createdAt completedAt sectionsJSON
    createdBy { id firstName lastName }
    completedBy{ id firstName lastName }
    sections {
      dailySourceInfo {
        sourceInformation
        sectionIsValid
        appVersion
      }
      workSchedule { startDatetime endDatetime }
      taskSelection {
        selectedTasks { id name riskLevel }
      }
      jobHazardAnalysis {
        siteConditions {
          id
          name
          isApplicable
          hazards {
            id
            name
            isApplicable
            controls {
              id
              name
              implemented
              notImplementedReason
              furtherExplanation
            }
          }
        }
        tasks {
          id
          name
          notes
          notApplicableReason
          performed
          hazards {
            id
            name
            isApplicable
            controls {
              id
              name
              implemented
              notImplementedReason
              furtherExplanation
            }
          }
        }
      },
      safetyAndCompliance
      crew {
        contractor
        foremanName
        nWelders
        nSafetyProf
        nOperators
        nFlaggers
        nLaborers
        nOtherCrew
        documents {
          date
          displayName
          name
          size
          time
          url
        }
      }
      additionalInformation {
        progress
        lessons
      }
      attachments {
        documents {
          date
          displayName
          name
          size
          time
          url
        }
        photos {
          date
          displayName
          name
          size
          time
          url
        }
      }
    }
  }
}
""",
}

save_daily_report_attachments_mutation = {
    "operation_name": "SaveDailyReport",
    "query": """
mutation SaveDailyReport($dailyReportInput: SaveDailyReportInput!) {
  saveDailyReport(dailyReportInput: $dailyReportInput) {
    sections {
      crew {
        documents {
          date
          displayName
          name
          size
          time
          url
          id
          signedUrl
          exists
        }
      }
      attachments {
        documents {
          category
          date
          displayName
          name
          size
          time
          url
          id
          signedUrl
          exists
        }
        photos {
          date
          displayName
          name
          size
          time
          url
          id
          signedUrl
          exists
        }
      }
    }
  }
}
""",
}

update_daily_report_status_mutation = {
    "operation_name": "UpdateDailyReportStatus",
    "query": """
mutation UpdateDailyReportStatus($id: UUID!, $status: FormStatus!) {
  updateDailyReportStatus(id: $id, status: $status) {
    id
    status
    completedBy { id name }
    completedAt
  }
}""",
}

delete_daily_report_mutation = {
    "operation_name": "DeleteDailyReport",
    "query": """
mutation DeleteDailyReport($id: UUID!) {
  deleteDailyReport(id: $id) }
  """,
}

example_file_inputs = [
    {
        "url": f"https://storage.googleapis.com/{settings.GS_BUCKET_NAME}/2022/01/01/blob-name",
        "name": "testfile1.pdf",
        "displayName": "testfile1.pdf",
        "size": "10kb",
        "date": "2022-01-01",
        "time": "1:00 PM",
    },
    {
        "url": f"https://storage.googleapis.com/{settings.GS_BUCKET_NAME}/2022/01/01/blob-name",
        "name": "testfile2.pdf",
        "displayName": "testfile2.pdf",
        "size": "10kb",
        "date": "2022-01-01",
        "time": "1:00 PM",
    },
    {
        "url": f"https://storage.googleapis.com/{settings.GS_BUCKET_NAME}/2022/01/01/blob-name",
        "name": "testfile3.pdf",
        "displayName": "testfile3.pdf",
        "size": "10kb",
        "date": "2022-01-01",
        "time": "1:00 PM",
    },
]


async def execute_delete_report(
    execute_gql: ExecuteGQL, id: uuid.UUID, raw: bool = False
) -> Any:
    response = await execute_gql(
        **delete_daily_report_mutation, variables={"id": id}, raw=raw
    )
    if raw:
        return response
    else:
        return response["deleteDailyReport"]


async def execute_update_status_report(
    execute_gql: ExecuteGQL,
    id: str | uuid.UUID,
    status: FormStatus,
    user: User | None = None,
) -> dict:
    response = await execute_gql(
        **update_daily_report_status_mutation,
        variables={"id": id, "status": status.name},
        user=user,
    )
    daily_report: dict = response["updateDailyReportStatus"]
    return daily_report


async def execute_get_report(
    execute_gql: ExecuteGQL,
    id: uuid.UUID | str,
    status: Optional[FormStatus] = None,
    raw: bool = False,
) -> Any:
    variables = {"id": id}
    if status:
        variables["status"] = status.name

    response = await execute_gql(
        **get_daily_report_query,
        variables=variables,
        raw=raw,
    )
    if raw:
        return response
    else:
        return response["dailyReport"]


async def execute_list_reports(
    execute_gql: ExecuteGQL,
    project_location_id: uuid.UUID,
    date: datetime.date,
    raw: bool = False,
) -> Any:
    response = await execute_gql(
        **get_daily_report_list_query,
        variables={"projectLocationId": project_location_id, "date": str(date)},
        raw=raw,
    )
    if raw:
        return response
    else:
        return response["dailyReports"]


async def execute_attachments(
    execute_gql: ExecuteGQL, data: dict, raw: bool = False, user: User | None = None
) -> Any:
    response = await execute_gql(
        **save_daily_report_attachments_mutation,
        variables={"dailyReportInput": data},
        raw=raw,
        user=user,
    )
    if raw:
        return response
    else:
        return response["saveDailyReport"]


async def execute_report(
    execute_gql: ExecuteGQL, data: dict, raw: bool = False, user: User | None = None
) -> Any:
    response = await execute_gql(
        **save_daily_report_mutation,
        variables={"dailyReportInput": data},
        raw=raw,
        user=user,
    )
    if raw:
        return response
    else:
        return response["saveDailyReport"]


async def build_report_data(
    db_session: AsyncSession, date: datetime.date | None = None
) -> tuple[dict, WorkPackage, Location]:
    project: WorkPackage = await WorkPackageFactory.persist(db_session)
    location: Location = await LocationFactory.persist(
        db_session, project_id=project.id
    )

    date = date or datetime.date.today()
    report_request = {
        "projectLocationId": str(location.id),
        "date": str(date),
        "dailySourceInfo": {
            "sourceInformation": "WEB_PORTAL",
            "sectionIsValid": None,
            "appVersion": "V1.1.1",
        },
    }
    return report_request, project, location


async def build_report_update_data(
    db_session: AsyncSession, user: User | None = None
) -> tuple[dict, DailyReport]:
    report_kwargs = {}
    if user:
        report_kwargs["created_by_id"] = user.id

    report: DailyReport = await DailyReportFactory.persist(db_session, **report_kwargs)
    report_data = {
        "id": str(report.id),
        "projectLocationId": str(report.project_location_id),
        "date": str(report.date_for),
    }
    return report_data, report


async def create_report(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    user: User | None = None,
    date: datetime.date | None = None,
) -> tuple[dict, dict]:
    report_request, *_ = await build_report_data(db_session, date=date)
    return report_request, await execute_report(execute_gql, report_request, user=user)
