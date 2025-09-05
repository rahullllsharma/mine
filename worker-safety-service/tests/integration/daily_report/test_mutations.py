import datetime
import uuid
from datetime import datetime as datetimenow

import pytest
from fastapi.encoders import jsonable_encoder
from sqlmodel import select

from tests.db_data import DBData
from tests.factories import (
    DailyReportFactory,
    LocationFactory,
    ManagerUserFactory,
    SiteConditionFactory,
    SupervisorUserFactory,
    WorkPackageFactory,
)
from tests.integration.conftest import ExecuteGQL
from tests.integration.daily_report.helpers import (
    create_report,
    execute_delete_report,
    execute_list_reports,
    execute_report,
    execute_update_status_report,
)
from worker_safety_service.models import (
    AsyncSession,
    DailyReport,
    DailyReportSections,
    DailyReportWorkSchedule,
    FormStatus,
    Location,
    WorkPackage,
)
from worker_safety_service.models.concepts import (
    DailySourceInformationConcepts,
    SourceAppInformation,
)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_create_mutation(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    # Call without ID should create the report
    report_request, report = await create_report(execute_gql, db_session)
    db_report = await db_data.daily_report(report["id"])
    assert db_report.id == uuid.UUID(report["id"])
    assert db_report.project_location_id == uuid.UUID(
        report_request["projectLocationId"]
    )
    assert str(db_report.date_for) == report_request["date"]
    sections = db_report.sections_to_pydantic()
    assert sections
    assert sections.work_schedule is None
    assert report["sections"]["workSchedule"] is None
    assert report["sections"]["taskSelection"] is None
    assert report["sections"]["jobHazardAnalysis"] is None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_update_mutation(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    report_request, report = await create_report(execute_gql, db_session)
    report_request["id"] = report["id"]

    # Call with ID should update the report
    date = str(datetime.datetime.utcnow())
    report_request["workSchedule"] = {"startDatetime": date}
    response = await execute_report(execute_gql, report_request)
    db_report = await db_data.daily_report(report["id"])
    assert report["id"] == response["id"]
    sections = db_report.sections_to_pydantic()
    assert sections
    assert sections.work_schedule is not None
    assert str(sections.work_schedule.start_datetime) == date
    assert sections.task_selection is None
    assert sections.job_hazard_analysis is None

    # Invalid ID should raise an error
    report_request["id"] = str(uuid.uuid4())
    response = await execute_report(execute_gql, report_request, raw=True)
    assert response.json().get("errors"), "No ID error raised"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_update_date(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    previous_date = datetime.date.today()
    report_request, report = await create_report(
        execute_gql, db_session, date=previous_date
    )
    report_request["id"] = report["id"]
    assert report["date"] == str(previous_date)
    reports = await execute_list_reports(
        execute_gql=execute_gql,
        project_location_id=report_request["projectLocationId"],
        date=previous_date,
    )
    assert report["id"] in [i["id"] for i in reports]

    # BE should allow to update the date
    date = previous_date + datetime.timedelta(days=1)
    report_request["date"] = str(date)
    report = await execute_report(execute_gql, report_request)
    assert report["date"] == str(date)

    # Should only show on new date
    reports = await execute_list_reports(
        execute_gql=execute_gql,
        project_location_id=report_request["projectLocationId"],
        date=previous_date,
    )
    assert report["id"] not in [i["id"] for i in reports]
    reports = await execute_list_reports(
        execute_gql=execute_gql,
        project_location_id=report_request["projectLocationId"],
        date=date,
    )
    assert report["id"] in [i["id"] for i in reports]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_update_date_with_jha_validation(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    previous_date = datetime.date.today()
    report_request, report = await create_report(
        execute_gql, db_session, date=previous_date
    )
    report_request["id"] = report["id"]

    # Add JHA site conditions that live on previous_date
    manual_ids = [
        str(i.id)
        for i in await SiteConditionFactory.persist_many(
            db_session, size=2, location_id=report_request["projectLocationId"]
        )
    ]
    evaluated_id = str(
        (
            await SiteConditionFactory.persist_evaluated(
                db_session,
                date=previous_date,
                location_id=report_request["projectLocationId"],
            )
        ).id
    )
    today_ids = set(manual_ids + [evaluated_id])
    report_request["jobHazardAnalysis"] = {
        "siteConditions": [
            {"id": i, "isApplicable": True, "hazards": []} for i in today_ids
        ],
        "tasks": [],
    }
    report = await execute_report(execute_gql, report_request)
    assert today_ids == {
        i["id"] for i in report["sections"]["jobHazardAnalysis"]["siteConditions"]
    }

    # Should fail if the user updates the date without updating JHA to valid ID's
    date = previous_date + datetime.timedelta(days=1)
    report_request["date"] = str(date)
    response = (await execute_report(execute_gql, report_request, raw=True)).json()
    assert evaluated_id in response["errors"][0]["message"]

    # Date shouldn't be updated after error
    await db_session.commit()
    db_report = await db_data.daily_report(report["id"])
    assert db_report.date_for == previous_date

    # We need to fix (or just clear) JHA to update the date
    report_request["jobHazardAnalysis"]["siteConditions"] = []
    report = await execute_report(execute_gql, report_request)
    assert report["date"] == str(date)
    assert report["sections"]["jobHazardAnalysis"]["siteConditions"] == []

    # Should only show on new date
    reports = await execute_list_reports(
        execute_gql=execute_gql,
        project_location_id=report_request["projectLocationId"],
        date=previous_date,
    )
    assert report["id"] not in [i["id"] for i in reports]
    reports = await execute_list_reports(
        execute_gql=execute_gql,
        project_location_id=report_request["projectLocationId"],
        date=date,
    )
    assert report["id"] in [i["id"] for i in reports]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_mutation_init_fields_blocked(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    report_request, report = await create_report(execute_gql, db_session)
    report_request["id"] = report["id"]

    # Not allowed to update project location id
    project: WorkPackage = await WorkPackageFactory.persist(db_session)
    location: Location = await LocationFactory.persist(
        db_session, project_id=project.id
    )
    date_update = {**report_request, "projectLocationId": str(location.id)}
    response = await execute_report(execute_gql, date_update, raw=True)
    assert response.json().get("errors"), "No projectLocationId error raised"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_update_status_mutation(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    user = await SupervisorUserFactory.persist(db_session)
    report = await DailyReportFactory.persist(db_session, created_by_id=user.id)
    assert report.status == FormStatus.IN_PROGRESS
    assert report.created_by_id == user.id
    assert report.archived_at is None
    report_sections = report.sections_to_pydantic()
    assert report_sections
    assert report_sections.completions in [None, []]

    # to COMPLETE
    response = await execute_update_status_report(
        execute_gql, report.id, FormStatus.COMPLETE, user=user
    )
    assert response["status"] == FormStatus.COMPLETE.name
    assert response["completedBy"]["id"] == str(user.id)
    assert response["completedAt"] is not None
    completed_at = datetime.datetime.fromisoformat(response["completedAt"])
    await db_session.refresh(report)
    assert report.status == FormStatus.COMPLETE
    assert report.completed_by_id == user.id
    assert report.completed_at == completed_at
    assert report.archived_at is None
    report_sections = report.sections_to_pydantic()
    assert report_sections
    assert report_sections.completions
    assert len(report_sections.completions) == 1
    assert report_sections.completions[0].completed_by_id == user.id
    assert report_sections.completions[0].completed_at == completed_at

    # back to IN_PROGRESS
    response = await execute_update_status_report(
        execute_gql, report.id, FormStatus.IN_PROGRESS, user=user
    )
    assert response["status"] == FormStatus.IN_PROGRESS.name
    assert response["completedBy"]["id"] == str(user.id)
    assert response["completedAt"] == completed_at.isoformat()
    await db_session.refresh(report)
    assert report.status == FormStatus.IN_PROGRESS
    assert report.completed_by_id == user.id
    assert report.completed_at == completed_at
    assert report.archived_at is None
    assert report_sections
    assert report_sections.completions
    assert len(report_sections.completions) == 1
    assert report_sections.completions[0].completed_by_id == user.id
    assert report_sections.completions[0].completed_at == completed_at

    # no update
    response = await execute_update_status_report(
        execute_gql, report.id, FormStatus.IN_PROGRESS, user=user
    )
    assert response["status"] == FormStatus.IN_PROGRESS.name
    assert response["completedBy"]["id"] == str(user.id)
    assert response["completedAt"] == completed_at.isoformat()
    await db_session.refresh(report)
    assert report.status == FormStatus.IN_PROGRESS
    assert report.completed_by_id == user.id
    assert report.completed_at == completed_at
    assert report.archived_at is None
    assert report_sections
    assert report_sections.completions
    assert len(report_sections.completions) == 1
    assert report_sections.completions[0].completed_by_id == user.id
    assert report_sections.completions[0].completed_at == completed_at

    # to COMPLETE
    other_user = await SupervisorUserFactory.persist(db_session)
    response = await execute_update_status_report(
        execute_gql, report.id, FormStatus.COMPLETE, user=other_user
    )
    assert response["status"] == FormStatus.COMPLETE.name
    assert response["completedBy"]["id"] == str(user.id)  # still using original user
    assert (
        response["completedAt"] == completed_at.isoformat()
    )  # still using original completed_at
    await db_session.refresh(report)
    assert report.status == FormStatus.COMPLETE
    assert report.completed_by_id == user.id  # still using original user
    assert report.completed_at == completed_at  # still using original completed_at
    assert report.archived_at is None
    report_sections = report.sections_to_pydantic()
    assert report_sections
    assert report_sections.completions
    assert len(report_sections.completions) == 2
    assert report_sections.completions[0].completed_by_id == user.id
    assert report_sections.completions[0].completed_at == completed_at
    assert report_sections.completions[1].completed_by_id == other_user.id
    assert report_sections.completions[1].completed_at
    assert report_sections.completions[1].completed_at > completed_at


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_reset_status_mutation(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """When a daily report is COMPLETE, updating it should set status to IN_PROGRESS"""

    user = await SupervisorUserFactory.persist(db_session)
    report_request, report = await create_report(execute_gql, db_session, user=user)
    report_request["id"] = report["id"]
    response = await execute_update_status_report(
        execute_gql, report["id"], FormStatus.COMPLETE, user=user
    )
    assert response["status"] == FormStatus.COMPLETE.name
    assert response["completedBy"]["id"] == str(user.id)
    assert response["completedAt"] is not None
    db_report = await db_data.daily_report(report["id"])
    assert db_report.status == FormStatus.COMPLETE
    assert db_report.completed_by_id == user.id
    completed_at = datetime.datetime.fromisoformat(response["completedAt"])
    assert db_report.completed_at == completed_at
    assert db_report.archived_at is None
    report_sections = db_report.sections_to_pydantic()
    assert report_sections
    assert report_sections.completions
    assert len(report_sections.completions) == 1
    assert report_sections.completions[0].completed_by_id == user.id
    assert report_sections.completions[0].completed_at == completed_at

    # Updating should set status to IN_PROGRESS
    assert not report_request.get("status")
    response = await execute_report(execute_gql, report_request)
    assert response["status"] == FormStatus.IN_PROGRESS.name
    assert response["completedBy"]["id"] == str(user.id)
    assert response["completedAt"] == completed_at.isoformat()
    await db_session.refresh(db_report)
    assert db_report.status == FormStatus.IN_PROGRESS
    assert db_report.completed_by_id == user.id
    assert db_report.completed_at == completed_at
    assert db_report.archived_at is None
    report_sections = db_report.sections_to_pydantic()
    assert report_sections
    assert report_sections.completions
    assert len(report_sections.completions) == 1
    assert report_sections.completions[0].completed_by_id == user.id
    assert report_sections.completions[0].completed_at == completed_at


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_delete_mutation(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    report = await DailyReportFactory.persist(db_session)
    assert report.archived_at is None
    response = await execute_delete_report(execute_gql, report.id)
    await db_session.refresh(report)
    assert response is True
    assert report.archived_at is not None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_db_data(db_session: AsyncSession) -> None:
    user = await ManagerUserFactory.persist(db_session)
    project_id: uuid.UUID = (await WorkPackageFactory.persist(db_session)).id
    location_id: uuid.UUID = (
        await LocationFactory.persist(db_session, project_id=project_id)
    ).id

    today = datetime.datetime.utcnow()
    appVersion = "v3.1.1"
    section_valid = True
    sourceInfo = SourceAppInformation.WEB_PORTAL
    report = DailyReport(
        project_location_id=location_id,
        created_by_id=user.id,
        date_for=datetime.date.today(),
        status=FormStatus.IN_PROGRESS,
        tenant_id=user.tenant_id,
        sections=jsonable_encoder(
            DailyReportSections(
                work_schedule=DailyReportWorkSchedule(
                    start_datetime=today,
                    end_datetime=today,
                ),
                dailySourceInfo=DailySourceInformationConcepts(
                    app_version=appVersion,
                    section_is_valid=section_valid,
                    source_information=sourceInfo,
                ),
            )
        ),
    )
    assert isinstance(report.status, FormStatus)

    # After adding, it should keep enum structure
    db_session.add(report)
    await db_session.commit()
    report_id = report.id
    assert isinstance(report.status, FormStatus)

    # Same for fetch
    statement = select(DailyReport).where(DailyReport.id == report_id)
    db_report: DailyReport | None = (await db_session.exec(statement)).first()
    assert db_report
    assert isinstance(db_report.status, FormStatus)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_update_mutation_with_dailySourceInfo(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    report_request, report = await create_report(execute_gql, db_session)
    report_request["id"] = report["id"]

    # Call with ID should update the report
    date = str(datetime.datetime.utcnow())
    report_request["workSchedule"] = {"startDatetime": date}
    response = await execute_report(execute_gql, report_request)

    assert response["sections"]["dailySourceInfo"]["appVersion"] == "V1.1.1"
    assert response["sections"]["dailySourceInfo"]["sourceInformation"] == "WEB_PORTAL"
    assert response["sections"]["dailySourceInfo"]["sectionIsValid"] is None


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_form_id_generation_daily_report_create_mutation(
    execute_gql: ExecuteGQL, db_session: AsyncSession, db_data: DBData
) -> None:
    daily_report_ids = []
    for _ in range(3):
        report_request, report = await create_report(execute_gql, db_session)
        db_report = await db_data.daily_report(report["id"])
        daily_report_ids.append(db_report.id)

    current_datetime = datetimenow.now()
    year_month = current_datetime.strftime("%y%m")

    for i, report_id in enumerate(daily_report_ids, start=1):
        expected_form_id = f"{year_month}{i:05}"
        db_report = await db_data.daily_report(report_id)
        assert db_report.form_id == expected_form_id
