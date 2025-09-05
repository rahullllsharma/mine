import asyncio
import uuid
from datetime import datetime, timezone
from typing import Union

import pytest
from fastapi import status
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from sqlalchemy.orm import sessionmaker
from sqlmodel import col, select

from tests.factories import (
    AdminUserFactory,
    LibrarySiteConditionFactory,
    LocationFactory,
    SiteConditionControlFactory,
    SiteConditionControlFactoryUrbRec,
    SiteConditionFactory,
    SiteConditionHazardFactory,
    SiteConditionHazardFactoryUrbRec,
    UserFactory,
)
from tests.integration.conftest import ExecuteGQL
from tests.integration.helpers import (
    assert_recent_datetime,
    gql_control,
    gql_hazard,
    gql_site_condition,
)
from worker_safety_service.dal.library import LibraryManager
from worker_safety_service.dal.library_site_conditions import (
    LibrarySiteConditionManager,
)
from worker_safety_service.dal.site_conditions import SiteConditionManager
from worker_safety_service.dal.user import UserManager
from worker_safety_service.models import (
    AsyncSession,
    Location,
    SiteCondition,
    SiteConditionControl,
    SiteConditionCreate,
    SiteConditionHazard,
)


async def fetch_site_condition(
    session: AsyncSession, id: Union[str, uuid.UUID]
) -> SiteCondition:
    statement = select(SiteCondition).where(SiteCondition.id == id)
    return (await session.exec(statement)).one()


async def fetch_hazard(
    session: AsyncSession, id: Union[str, uuid.UUID]
) -> SiteConditionHazard:
    statement = select(SiteConditionHazard).where(SiteConditionHazard.id == id)
    return (await session.exec(statement)).one()


async def fetch_hazards(
    session: AsyncSession, site_condition_id: Union[str, uuid.UUID]
) -> list[SiteConditionHazard]:
    statement = select(SiteConditionHazard).where(
        SiteConditionHazard.site_condition_id == site_condition_id
    )
    return (await session.exec(statement)).all()


async def fetch_control(
    session: AsyncSession, id: Union[str, uuid.UUID]
) -> SiteConditionControl:
    statement = select(SiteConditionControl).where(SiteConditionControl.id == id)
    return (await session.exec(statement)).one()


async def fetch_controls(
    session: AsyncSession, hazard_id: Union[str, uuid.UUID]
) -> list[SiteConditionControl]:
    statement = select(SiteConditionControl).where(
        SiteConditionControl.site_condition_hazard_id == hazard_id
    )
    return (await session.exec(statement)).all()


create_site_condition_mutation = {
    "operation_name": "CreateSiteCondition",
    "query": """
mutation CreateSiteCondition($siteCondition: CreateSiteConditionInput!) {
  siteCondition: createSiteCondition(data: $siteCondition) {
    id
    createdBy {
        id
    }
  }
}
""",
}


edit_site_condition_mutation = {
    "operation_name": "EditSiteCondition",
    "query": """
mutation EditSiteCondition($siteCondition: EditSiteConditionInput!) {
  siteCondition: editSiteCondition(data: $siteCondition) {
    id hazards {id isApplicable controls {id isApplicable}}}
}
""",
}


################################################################################
# Add a site_condition to a location
################################################################################


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_site_condition(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    # create an extra site_condition so we can use its relational data
    extra_site_condition: SiteCondition = await SiteConditionFactory.persist(db_session)
    library_site_condition_id: uuid.UUID = (
        await LibrarySiteConditionFactory.persist(db_session)
    ).id

    user = await AdminUserFactory.persist(db_session)
    site_condition: SiteCondition = SiteConditionFactory.build()

    data = await execute_gql(
        **create_site_condition_mutation,
        variables={
            "siteCondition": {
                **gql_site_condition(site_condition.dict(exclude={"id"})),
                "locationId": extra_site_condition.location_id,
                "librarySiteConditionId": library_site_condition_id,
            }
        },
        user=user,
    )

    site_condition_data = data["siteCondition"]

    fetched = await fetch_site_condition(db_session, site_condition_data["id"])
    assert fetched.location_id == extra_site_condition.location_id
    assert fetched.library_site_condition_id == library_site_condition_id
    assert str(fetched.user_id) == site_condition_data["createdBy"]["id"]
    assert fetched.is_manually_added is True


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_site_condition_with_archived_location(
    test_client: AsyncClient, db_session: AsyncSession
) -> None:
    """
    Asserts that an error is returned when a createSiteCondition mutation is attempted on
    an archived project location.
    """
    extra_site_condition: SiteCondition = await SiteConditionFactory.persist(db_session)
    location: Location = await LocationFactory.persist(db_session)
    location.archived_at = datetime.now(timezone.utc)
    await db_session.commit()

    site_condition: SiteCondition = SiteConditionFactory.build()

    post_data = {
        "operationName": create_site_condition_mutation["operation_name"],
        "query": create_site_condition_mutation["query"],
        "variables": jsonable_encoder(
            {
                "siteCondition": {
                    **gql_site_condition(site_condition.dict(exclude={"id"})),
                    # use the archived location
                    "locationId": location.id,
                    "librarySiteConditionId": extra_site_condition.library_site_condition_id,
                }
            }
        ),
    }

    response = await test_client.post("/graphql", json=post_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "errors" in data
    messages = [x["message"] for x in data["errors"]]
    assert "Project Location ID not found." in messages


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_site_condition_with_hazards(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    # extra models so we can use their relational data
    extra_site_condition: SiteCondition = await SiteConditionFactory.persist(db_session)
    library_site_condition_id: uuid.UUID = (
        await LibrarySiteConditionFactory.persist(db_session)
    ).id
    extra_hazard: SiteConditionHazard = await SiteConditionHazardFactory.persist(
        db_session
    )

    site_condition: SiteCondition = SiteConditionFactory.build()
    hazard: SiteConditionHazard = SiteConditionHazardFactory.build(is_applicable=True)

    new_hazard = {
        **gql_hazard(hazard.dict(exclude={"id"})),
        "libraryHazardId": extra_hazard.library_hazard_id,
    }
    data = await execute_gql(
        **create_site_condition_mutation,
        variables={
            "siteCondition": {
                **gql_site_condition(site_condition.dict(exclude={"id"})),
                "locationId": extra_site_condition.location_id,
                "librarySiteConditionId": library_site_condition_id,
                "hazards": [new_hazard],
            }
        },
    )

    site_condition_data = data["siteCondition"]

    fetched = await fetch_site_condition(db_session, site_condition_data["id"])
    assert fetched
    assert fetched.location_id == extra_site_condition.location_id
    assert fetched.library_site_condition_id == library_site_condition_id
    assert fetched.is_manually_added is True

    hazards = await fetch_hazards(db_session, site_condition_data["id"])
    assert len(hazards) == 1
    fetched_hazard = hazards[0]
    assert fetched_hazard.is_applicable == hazard.is_applicable
    assert fetched_hazard.library_hazard_id == extra_hazard.library_hazard_id
    assert fetched_hazard.position == 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_site_condition_with_hazard_and_control(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    # extra models so we can use their relational data
    extra_site_condition = await SiteConditionFactory.persist(db_session)
    library_site_condition_id: uuid.UUID = (
        await LibrarySiteConditionFactory.persist(db_session)
    ).id
    extra_hazard = await SiteConditionHazardFactory.persist(db_session)
    extra_control = await SiteConditionControlFactory.persist(db_session)

    site_condition = SiteConditionFactory.build()
    hazard = SiteConditionHazardFactory.build(is_applicable=True)
    control = SiteConditionControlFactory.build(is_applicable=True)

    new_hazard = {
        **gql_hazard(hazard.dict(exclude={"id"})),
        "libraryHazardId": extra_hazard.library_hazard_id,
        "controls": [
            {
                **gql_control(control.dict(exclude={"id"})),
                "libraryControlId": extra_control.library_control_id,
            }
        ],
    }
    data = await execute_gql(
        **create_site_condition_mutation,
        variables={
            "siteCondition": {
                **gql_site_condition(site_condition.dict(exclude={"id"})),
                "locationId": extra_site_condition.location_id,
                "librarySiteConditionId": library_site_condition_id,
                "hazards": [new_hazard],
            }
        },
    )

    site_condition_data = data["siteCondition"]

    fetched = await fetch_site_condition(db_session, site_condition_data["id"])
    assert fetched
    assert fetched.location_id == extra_site_condition.location_id
    assert fetched.library_site_condition_id == library_site_condition_id
    assert fetched.is_manually_added is True

    hazards = await fetch_hazards(db_session, site_condition_data["id"])
    assert len(hazards) == 1
    fetched_hazard = hazards[0]
    assert fetched_hazard.is_applicable == hazard.is_applicable
    assert fetched_hazard.library_hazard_id == extra_hazard.library_hazard_id
    assert fetched_hazard.position == 0

    controls = await fetch_controls(db_session, fetched_hazard.id)
    assert len(controls) == 1
    fetched_control = controls[0]
    assert fetched_control.is_applicable == control.is_applicable
    assert fetched_control.library_control_id == extra_control.library_control_id
    assert fetched_control.position == 0


################################################################################
# Edit Site Condition Hazards
################################################################################


@pytest.mark.asyncio
@pytest.mark.integration
async def test_edit_site_condition_hazard(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Asserts that a hazard's is_applicable field can be toggled.
    """
    site_condition: SiteCondition = await SiteConditionFactory.persist(db_session)
    hazard: SiteConditionHazard = await SiteConditionHazardFactoryUrbRec.persist(
        db_session, site_condition_id=site_condition.id
    )
    await db_session.refresh(site_condition)
    new_is_applicable = not hazard.is_applicable

    updated_hazard = {
        **gql_hazard(hazard),
        "isApplicable": new_is_applicable,
    }
    data = await execute_gql(
        **edit_site_condition_mutation,
        variables={
            "siteCondition": {"id": site_condition.id, "hazards": [updated_hazard]}
        },
    )

    assert data["siteCondition"]["id"] == str(site_condition.id)
    assert data["siteCondition"]["hazards"][0]["id"] == str(hazard.id)
    assert data["siteCondition"]["hazards"][0]["isApplicable"] == new_is_applicable

    await db_session.refresh(hazard)
    assert hazard.is_applicable == new_is_applicable


@pytest.mark.asyncio
@pytest.mark.integration
async def test_edit_site_condition_hazard_user_owned(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Asserts that a hazard's is_applicable field is not toggled if it has a user_id.
    """
    site_condition: SiteCondition = await SiteConditionFactory.persist(db_session)
    # allow a user_id to exist on this hazard
    hazard: SiteConditionHazard = await SiteConditionHazardFactory.persist(
        db_session,
        site_condition_id=site_condition.id,
        user_id=uuid.uuid4(),  # make sure user_id is set!
    )
    await db_session.refresh(site_condition)
    new_is_applicable = not hazard.is_applicable

    updated_hazard = {
        **gql_hazard(hazard),
        # attempt to update this value
        "isApplicable": new_is_applicable,
    }
    data = await execute_gql(
        **edit_site_condition_mutation,
        variables={
            "siteCondition": {"id": site_condition.id, "hazards": [updated_hazard]}
        },
    )

    assert data["siteCondition"]["id"] == str(site_condition.id)
    assert data["siteCondition"]["hazards"][0]["id"] == str(hazard.id)
    # here we make sure isApplicable was _not_ updated, because this hazard has a user_id
    assert data["siteCondition"]["hazards"][0]["isApplicable"] == (
        not new_is_applicable
    )

    await db_session.refresh(hazard)
    # here we make sure isApplicable was _not_ updated, because this hazard has a user_id
    assert hazard.is_applicable == (not new_is_applicable)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_edit_site_condition_add_hazard_append(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Asserts that a hazard added to a site_condition gets a correctly set 'position'.
    This hazard is appended to the current hazard list.
    """
    site_condition: SiteCondition = await SiteConditionFactory.persist(db_session)
    existing_hazard: SiteConditionHazard = (
        await SiteConditionHazardFactoryUrbRec.persist(
            db_session,
            site_condition_id=site_condition.id,
        )
    )
    new_hazard: SiteConditionHazard = await SiteConditionHazardFactoryUrbRec.persist(
        db_session
    )
    await db_session.refresh(site_condition)
    await db_session.refresh(existing_hazard)
    await db_session.refresh(new_hazard)

    new = {**gql_hazard(new_hazard), "isApplicable": True}
    del new["id"]

    data = await execute_gql(
        **edit_site_condition_mutation,
        variables={
            "siteCondition": {
                **gql_site_condition(site_condition),
                "hazards": [
                    {**gql_hazard(existing_hazard), "isApplicable": True},
                    new,
                ],
            }
        },
    )

    assert data["siteCondition"]["id"] == str(site_condition.id)
    assert len(data["siteCondition"]["hazards"]) == 2
    hazards = await fetch_hazards(db_session, data["siteCondition"]["id"])
    assert len(hazards) == 2
    for haz in hazards:
        # refresh, b/c apparently fetch still uses cached data
        await db_session.refresh(haz)
        assert haz.position is not None
        if haz.id == existing_hazard.id:
            assert haz.position == 0
        else:
            assert haz.position == 1


@pytest.mark.asyncio
@pytest.mark.integration
async def test_edit_site_condition_add_hazard_prepend(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Asserts that a hazard added to a site_condition gets a correctly set 'position'.
    This hazard is prepended to the existing hazard list.
    """
    site_condition: SiteCondition = await SiteConditionFactory.persist(db_session)
    existing_hazard: SiteConditionHazard = (
        await SiteConditionHazardFactoryUrbRec.persist(
            db_session,
            site_condition_id=site_condition.id,
        )
    )
    new_hazard: SiteConditionHazard = await SiteConditionHazardFactoryUrbRec.persist(
        db_session
    )
    await db_session.refresh(site_condition)
    await db_session.refresh(existing_hazard)
    await db_session.refresh(new_hazard)

    new = {**gql_hazard(new_hazard), "isApplicable": True}
    del new["id"]

    data = await execute_gql(
        **edit_site_condition_mutation,
        variables={
            "siteCondition": {
                **gql_site_condition(site_condition),
                "hazards": [
                    new,
                    {**gql_hazard(existing_hazard), "isApplicable": True},
                ],
            }
        },
    )

    assert data["siteCondition"]["id"] == str(site_condition.id)
    assert len(data["siteCondition"]["hazards"]) == 2
    hazards = await fetch_hazards(db_session, data["siteCondition"]["id"])
    assert len(hazards) == 2
    for haz in hazards:
        # refresh, b/c apparently fetch still uses cached data
        await db_session.refresh(haz)
        assert haz.position is not None
        if haz.id == existing_hazard.id:
            assert haz.position == 1
        else:
            assert haz.position == 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_edit_site_condition_add_hazard_insert(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Asserts that a hazard added to a site_condition gets a correctly set 'position'.
    This hazard is inserted in the middle of the existing hazard list.
    """
    site_condition = await SiteConditionFactory.persist(db_session)
    existing_hazards = await SiteConditionHazardFactoryUrbRec.persist_many(
        db_session, site_condition_id=site_condition.id, size=2
    )
    new_hazard = await SiteConditionHazardFactoryUrbRec.persist(db_session)
    await db_session.refresh(site_condition)
    for task_haz in existing_hazards:
        await db_session.refresh(task_haz)
    await db_session.refresh(new_hazard)

    new = {**gql_hazard(new_hazard), "isApplicable": True}
    del new["id"]

    data = await execute_gql(
        **edit_site_condition_mutation,
        variables={
            "siteCondition": {
                **gql_site_condition(site_condition),
                "hazards": [
                    {**gql_hazard(existing_hazards[0]), "isApplicable": True},
                    new,
                    {**gql_hazard(existing_hazards[1]), "isApplicable": True},
                ],
            }
        },
    )

    assert data["siteCondition"]["id"] == str(site_condition.id)
    assert len(data["siteCondition"]["hazards"]) == 3
    hazards = await fetch_hazards(db_session, data["siteCondition"]["id"])
    assert len(hazards) == 3
    for haz in hazards:
        # refresh, b/c apparently fetch still uses cached data
        await db_session.refresh(haz)
        assert haz.position is not None
        if haz.id in {i.id for i in existing_hazards}:
            assert haz.position == 0 or haz.position == 2
        else:
            assert haz.position == 1


################################################################################
# Edit Site Condition Controls
################################################################################


@pytest.mark.asyncio
@pytest.mark.integration
async def test_edit_site_condition_control(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Asserts that a controls's is_applicable field can be toggled.
    """
    site_condition: SiteCondition = await SiteConditionFactory.persist(db_session)
    hazard: SiteConditionHazard = await SiteConditionHazardFactory.persist(
        db_session,
        site_condition_id=site_condition.id,
    )
    control: SiteConditionControl = await SiteConditionControlFactoryUrbRec.persist(
        db_session, site_condition_hazard_id=hazard.id
    )
    await db_session.refresh(hazard)
    await db_session.refresh(site_condition)
    new_is_applicable = not control.is_applicable

    updated_hazard = {
        **gql_hazard(hazard),
        "controls": [{**gql_control(control), "isApplicable": new_is_applicable}],
    }
    data = await execute_gql(
        **edit_site_condition_mutation,
        variables={
            "siteCondition": {"id": site_condition.id, "hazards": [updated_hazard]}
        },
    )

    assert data["siteCondition"]["id"] == str(site_condition.id)
    assert data["siteCondition"]["hazards"][0]["controls"][0]["id"] == str(control.id)
    assert (
        data["siteCondition"]["hazards"][0]["controls"][0]["isApplicable"]
        == new_is_applicable
    )

    await db_session.refresh(control)
    assert control.is_applicable == new_is_applicable


@pytest.mark.asyncio
@pytest.mark.integration
async def test_edit_site_condition_control_user_owned(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Asserts that a controls's is_applicable field cannot be toggled if it has a user_id.
    """
    site_condition: SiteCondition = await SiteConditionFactory.persist(db_session)
    hazard: SiteConditionHazard = await SiteConditionHazardFactory.persist(
        db_session,
        site_condition_id=site_condition.id,
    )
    # allow a user_id to exist on this control
    control: SiteConditionControl = await SiteConditionControlFactory.persist(
        db_session,
        site_condition_hazard_id=hazard.id,
        user_id=uuid.uuid4(),  # make sure user_id is set!
    )
    await db_session.refresh(hazard)
    await db_session.refresh(site_condition)
    new_is_applicable = not control.is_applicable

    updated_hazard = {
        **gql_hazard(hazard),
        "controls": [{**gql_control(control), "isApplicable": new_is_applicable}],
    }
    data = await execute_gql(
        **edit_site_condition_mutation,
        variables={
            "siteCondition": {"id": site_condition.id, "hazards": [updated_hazard]}
        },
    )

    # assert the control's is_applicable has NOT changed

    assert data["siteCondition"]["id"] == str(site_condition.id)
    assert data["siteCondition"]["hazards"][0]["controls"][0]["id"] == str(control.id)
    assert data["siteCondition"]["hazards"][0]["controls"][0]["isApplicable"] == (
        not new_is_applicable
    )

    await db_session.refresh(control)
    assert control.is_applicable == (not new_is_applicable)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_edit_site_condition_add_control_append(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Asserts that a control added to a site_condition gets a correctly set 'position'.
    This control is appended to the current control list.
    """
    site_condition: SiteCondition = await SiteConditionFactory.persist(db_session)
    hazard: SiteConditionHazard = await SiteConditionHazardFactory.persist(
        db_session,
        site_condition_id=site_condition.id,
    )
    existing_control = await SiteConditionControlFactory.persist(
        db_session,
        site_condition_hazard_id=hazard.id,
    )
    new_control = await SiteConditionControlFactory.persist(db_session)
    await db_session.refresh(site_condition)
    await db_session.refresh(hazard)
    await db_session.refresh(existing_control)
    await db_session.refresh(new_control)

    new = {**gql_control(new_control), "isApplicable": True}
    del new["id"]

    data = await execute_gql(
        **edit_site_condition_mutation,
        variables={
            "siteCondition": {
                **gql_site_condition(site_condition),
                "hazards": [
                    {
                        **gql_hazard(hazard),
                        "isApplicable": True,
                        "controls": [
                            {**gql_control(existing_control), "isApplicable": True},
                            new,
                        ],
                    },
                ],
            }
        },
    )

    assert data["siteCondition"]["id"] == str(site_condition.id)
    assert len(data["siteCondition"]["hazards"]) == 1
    assert len(data["siteCondition"]["hazards"][0]["controls"]) == 2
    controls = await fetch_controls(
        db_session, data["siteCondition"]["hazards"][0]["id"]
    )
    assert len(controls) == 2
    for control in controls:
        # refresh, b/c apparently fetch still uses cached data
        await db_session.refresh(control)
        assert control.position is not None
        if control.id == existing_control.id:
            assert control.position == 0
        else:
            assert control.position == 1


@pytest.mark.asyncio
@pytest.mark.integration
async def test_edit_site_condition_add_control_prepend(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Asserts that a control added to a site_condition gets a correctly set 'position'.
    This control is appended to the current control list.
    """
    site_condition: SiteCondition = await SiteConditionFactory.persist(db_session)
    hazard: SiteConditionHazard = await SiteConditionHazardFactory.persist(
        db_session,
        site_condition_id=site_condition.id,
    )
    existing_control = await SiteConditionControlFactory.persist(
        db_session,
        site_condition_hazard_id=hazard.id,
    )
    new_control = await SiteConditionControlFactory.persist(db_session)
    await db_session.refresh(site_condition)
    await db_session.refresh(hazard)
    await db_session.refresh(existing_control)
    await db_session.refresh(new_control)

    new = {**gql_control(new_control), "isApplicable": True}
    del new["id"]

    data = await execute_gql(
        **edit_site_condition_mutation,
        variables={
            "siteCondition": {
                **gql_site_condition(site_condition),
                "hazards": [
                    {
                        **gql_hazard(hazard),
                        "isApplicable": True,
                        "controls": [
                            new,
                            {**gql_control(existing_control), "isApplicable": True},
                        ],
                    },
                ],
            }
        },
    )

    assert data["siteCondition"]["id"] == str(site_condition.id)
    assert len(data["siteCondition"]["hazards"]) == 1
    assert len(data["siteCondition"]["hazards"][0]["controls"]) == 2
    controls = await fetch_controls(
        db_session, data["siteCondition"]["hazards"][0]["id"]
    )
    assert len(controls) == 2
    for control in controls:
        # refresh, b/c apparently fetch still uses cached data
        await db_session.refresh(control)
        assert control.position is not None
        if control.id == existing_control.id:
            assert control.position == 1
        else:
            assert control.position == 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_edit_site_condition_add_control_insert(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Asserts that a control added to a site_condition gets a correctly set 'position'.
    This control is inserted to the middle of current control list.
    """
    site_condition: SiteCondition = await SiteConditionFactory.persist(db_session)
    hazard: SiteConditionHazard = await SiteConditionHazardFactory.persist(
        db_session,
        site_condition_id=site_condition.id,
    )
    existing_controls = await SiteConditionControlFactory.persist_many(
        db_session, site_condition_hazard_id=hazard.id, size=2
    )
    new_control = await SiteConditionControlFactory.persist(db_session)
    await db_session.refresh(site_condition)
    await db_session.refresh(hazard)
    for existing_control in existing_controls:
        await db_session.refresh(existing_control)
    await db_session.refresh(new_control)

    new = {**gql_control(new_control), "isApplicable": True}
    del new["id"]

    data = await execute_gql(
        **edit_site_condition_mutation,
        variables={
            "siteCondition": {
                **gql_site_condition(site_condition),
                "hazards": [
                    {
                        **gql_hazard(hazard),
                        "isApplicable": True,
                        "controls": [
                            {**gql_control(existing_controls[0]), "isApplicable": True},
                            new,
                            {**gql_control(existing_controls[1]), "isApplicable": True},
                        ],
                    },
                ],
            }
        },
    )

    assert data["siteCondition"]["id"] == str(site_condition.id)
    assert len(data["siteCondition"]["hazards"]) == 1
    assert len(data["siteCondition"]["hazards"][0]["controls"]) == 3
    controls = await fetch_controls(
        db_session, data["siteCondition"]["hazards"][0]["id"]
    )
    assert len(controls) == 3
    for control in controls:
        # refresh, b/c apparently fetch still uses cached data
        await db_session.refresh(control)
        assert control.position is not None
        if control.id in {i.id for i in existing_controls}:
            assert control.position == 0 or control.position == 2
        else:
            assert control.position == 1


################################################################################
# Archive an existing site_condition
################################################################################


@pytest.mark.asyncio
@pytest.mark.integration
async def test_archive_site_condition(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    site_condition: SiteCondition = await SiteConditionFactory.persist(db_session)

    delete_site_condition_mutation = {
        "operation_name": "DeleteSiteCondition",
        "query": "mutation DeleteSiteCondition($id: UUID!) { siteCondition: deleteSiteCondition(id: $id) }",
    }

    data = await execute_gql(
        **delete_site_condition_mutation, variables={"id": site_condition.id}
    )

    assert data["siteCondition"]  # our current response is a boolean

    # ensure the site_condition still exists in the db, and is archived
    await db_session.refresh(site_condition)
    assert_recent_datetime(site_condition.archived_at)

    # fetch a new version of the same obj.
    archived = await fetch_site_condition(db_session, site_condition.id)
    assert_recent_datetime(archived.archived_at)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_archive_site_condition_archives_nested_objs(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Asserts that archiving a site_condition also archives it's hazards and controls.
    """
    site_condition: SiteCondition = await SiteConditionFactory.persist(db_session)
    rec_hazard: SiteConditionHazard = await SiteConditionHazardFactory.persist(
        db_session,
        site_condition_id=site_condition.id,
        user_id=None,
    )
    rec_control: SiteConditionControl = await SiteConditionControlFactory.persist(
        db_session,
        site_condition_hazard_id=rec_hazard.id,
        user_id=None,
    )
    user_id = uuid.uuid4()
    user_hazard: SiteConditionHazard = await SiteConditionHazardFactory.persist(
        db_session,
        site_condition_id=site_condition.id,
        user_id=user_id,
    )
    user_control: SiteConditionControl = await SiteConditionControlFactory.persist(
        db_session,
        site_condition_hazard_id=user_hazard.id,
        user_id=user_id,
    )
    await db_session.refresh(site_condition)

    delete_site_condition_mutation = {
        "operation_name": "DeleteSiteCondition",
        "query": "mutation DeleteSiteCondition($id: UUID!) { siteCondition: deleteSiteCondition(id: $id) }",
    }

    data = await execute_gql(
        **delete_site_condition_mutation, variables={"id": site_condition.id}
    )
    assert data["siteCondition"]  # our current response is a boolean

    # ensure the objs still exist in the db, and have archived_at set
    for d in [site_condition, rec_hazard, rec_control, user_hazard, user_control]:
        await db_session.refresh(d)
        assert_recent_datetime(d.archived_at)  # type: ignore


@pytest.mark.asyncio
@pytest.mark.integration
async def test_archive_site_condition_hazard(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Creates a site_condition and hazard, then sends an editSiteCondition mutation without that hazard,
    triggering an archive. Also asserts that recommended and user-owned controls
    are archived.
    """

    site_condition: SiteCondition = await SiteConditionFactory.persist(db_session)
    hazard: SiteConditionHazard = await SiteConditionHazardFactory.persist(
        db_session,
        site_condition_id=site_condition.id,
        user_id=uuid.uuid4(),  # make sure user_id is set!
    )
    rec_control: SiteConditionControl = await SiteConditionControlFactory.persist(
        db_session,
        site_condition_hazard_id=hazard.id,
        user_id=None,
    )
    user_control: SiteConditionControl = await SiteConditionControlFactory.persist(
        db_session,
        site_condition_hazard_id=hazard.id,
        user_id=None,
    )
    await db_session.refresh(site_condition)

    data = await execute_gql(
        **edit_site_condition_mutation,
        variables={"siteCondition": {"id": site_condition.id, "hazards": []}},
    )

    assert data["siteCondition"]["id"] == str(site_condition.id)
    assert len(data["siteCondition"]["hazards"]) == 0

    await db_session.refresh(hazard)
    assert_recent_datetime(hazard.archived_at)

    # fetch a new version of the same obj.
    archived = await fetch_hazard(db_session, hazard.id)
    assert_recent_datetime(archived.archived_at)

    for d in [rec_control, user_control]:
        await db_session.refresh(d)
        assert_recent_datetime(d.archived_at)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_archive_site_condition_hazard_user_owned(
    test_client: AsyncClient, db_session: AsyncSession
) -> None:
    """
    Prevents archiving a hazard that is not user_owned.
    """

    site_condition: SiteCondition = await SiteConditionFactory.persist(db_session)
    hazard: SiteConditionHazard = await SiteConditionHazardFactoryUrbRec.persist(
        db_session, site_condition_id=site_condition.id
    )
    await db_session.refresh(site_condition)

    post_data = {
        "operationName": edit_site_condition_mutation["operation_name"],
        "query": edit_site_condition_mutation["query"],
        "variables": jsonable_encoder(
            {"siteCondition": {"id": site_condition.id, "hazards": []}}
        ),
    }

    response = await test_client.post("/graphql", json=post_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "errors" in data

    message = data["errors"][0]["message"]
    assert "Not allowed to remove" in message

    await db_session.refresh(hazard)
    assert hazard.archived_at is None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_archive_site_condition_hazard_updates_positions(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Asserts that archiving a hazard on a site_condition updates 'position' on the remaining hazards.
    """
    site_condition: SiteCondition = await SiteConditionFactory.persist(db_session)
    existing_hazards = await SiteConditionHazardFactory.persist_many(
        db_session,
        site_condition_id=site_condition.id,
        size=3,
        user_id=uuid.uuid4(),  # make sure user_id is set!
    )
    to_archive = existing_hazards[1]
    await db_session.refresh(site_condition)
    for haz in existing_hazards:
        await db_session.refresh(haz)

    data = await execute_gql(
        **edit_site_condition_mutation,
        variables={
            "siteCondition": {
                **gql_site_condition(site_condition),
                "hazards": [
                    {**gql_hazard(existing_hazards[0]), "isApplicable": True},
                    # dropping existing_hazards[1]
                    {**gql_hazard(existing_hazards[2]), "isApplicable": True},
                ],
            }
        },
    )

    assert data["siteCondition"]["id"] == str(site_condition.id)
    assert len(data["siteCondition"]["hazards"]) == 2
    # note this fetch includes archived hazards
    hazards = await fetch_hazards(db_session, data["siteCondition"]["id"])
    assert len(hazards) == 3
    for haz in hazards:
        # refresh, b/c apparently fetch still uses cached data
        await db_session.refresh(haz)
        assert haz.position is not None
        if not haz.archived_at:
            assert haz.position == 0 or haz.position == 1
        elif not haz.id == to_archive.id:
            # sanity check
            assert False, "Missing expected hazard in test!"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_archive_site_condition_control(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Creates a site_condition, hazard, and control, then sends an editSiteCondition mutation without
    the control, triggering an archive.
    """

    site_condition: SiteCondition = await SiteConditionFactory.persist(db_session)
    hazard: SiteConditionHazard = await SiteConditionHazardFactory.persist(
        db_session,
        site_condition_id=site_condition.id,
    )
    control: SiteConditionControl = await SiteConditionControlFactory.persist(
        db_session,
        site_condition_hazard_id=hazard.id,
        user_id=uuid.uuid4(),
    )
    await db_session.refresh(site_condition)
    await db_session.refresh(hazard)

    data = await execute_gql(
        **edit_site_condition_mutation,
        variables={
            "siteCondition": {
                "id": site_condition.id,
                "hazards": [{**gql_hazard(hazard), "controls": []}],
            }
        },
    )

    assert data["siteCondition"]["id"] == str(site_condition.id)
    assert len(data["siteCondition"]["hazards"][0]["controls"]) == 0

    await db_session.refresh(control)
    assert_recent_datetime(control.archived_at)

    # fetch a new version of the same obj.
    archived = await fetch_control(db_session, control.id)
    assert_recent_datetime(archived.archived_at)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_archive_site_condition_control_user_owned(
    test_client: AsyncClient, db_session: AsyncSession
) -> None:
    """
    Prevents archiving a hazard that is not user_owned.
    """

    site_condition: SiteCondition = await SiteConditionFactory.persist(db_session)
    hazard: SiteConditionHazard = await SiteConditionHazardFactory.persist(
        db_session,
        site_condition_id=site_condition.id,
    )
    control: SiteConditionControl = await SiteConditionControlFactoryUrbRec.persist(
        db_session, site_condition_hazard_id=hazard.id
    )
    await db_session.refresh(site_condition)
    await db_session.refresh(hazard)

    post_data = {
        "operationName": edit_site_condition_mutation["operation_name"],
        "query": edit_site_condition_mutation["query"],
        "variables": jsonable_encoder(
            {
                "siteCondition": {
                    "id": site_condition.id,
                    "hazards": [{**gql_hazard(hazard), "controls": []}],
                }
            }
        ),
    }

    response = await test_client.post("/graphql", json=post_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "errors" in data

    message = data["errors"][0]["message"]
    assert "Not allowed to remove" in message

    await db_session.refresh(control)
    assert control.archived_at is None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_archive_site_condition_control_updates_positions(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Asserts that archiving a control on a site_condition updates 'position' on the remaining controls.
    """
    site_condition: SiteCondition = await SiteConditionFactory.persist(db_session)
    hazard = await SiteConditionHazardFactory.persist(
        db_session, site_condition_id=site_condition.id
    )
    existing_controls = await SiteConditionControlFactory.persist_many(
        db_session,
        site_condition_hazard_id=hazard.id,
        size=3,
        user_id=uuid.uuid4(),  # make sure user_id is set!
    )
    to_archive = existing_controls[1]
    await db_session.refresh(site_condition)
    await db_session.refresh(hazard)
    for ctrl in existing_controls:
        await db_session.refresh(ctrl)

    data = await execute_gql(
        **edit_site_condition_mutation,
        variables={
            "siteCondition": {
                **gql_site_condition(site_condition),
                "hazards": [
                    {
                        **gql_hazard(hazard),
                        "controls": [
                            {**gql_control(existing_controls[0]), "isApplicable": True},
                            # dropping existing_hazards[1]
                            {**gql_control(existing_controls[2]), "isApplicable": True},
                        ],
                    }
                ],
            }
        },
    )

    assert data["siteCondition"]["id"] == str(site_condition.id)
    assert len(data["siteCondition"]["hazards"]) == 1
    assert len(data["siteCondition"]["hazards"][0]["controls"]) == 2
    # note this fetch includes archived controls
    controls = await fetch_controls(
        db_session, data["siteCondition"]["hazards"][0]["id"]
    )
    assert len(controls) == 3
    for control in controls:
        # refresh, b/c apparently fetch still uses cached data
        await db_session.refresh(control)
        assert control.position is not None
        if not control.archived_at:
            assert control.position == 0 or control.position == 1
        elif not control.id == to_archive.id:
            # sanity check
            assert False, "Missing expected control in test!"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_archive_site_condition_hazards_and_controls_only_once(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Creates a site_condition, hazard, and control, then sends an
    editSiteCondition mutation without the hazard or control, triggering an
    archive of both. Sends the query a second time and ensures the archived_at
    hasn't fired twice. Prevents re-archiving of hazards and controls.
    """

    site_condition: SiteCondition = await SiteConditionFactory.persist(db_session)
    hazard: SiteConditionHazard = await SiteConditionHazardFactory.persist(
        db_session,
        site_condition_id=site_condition.id,
    )
    control: SiteConditionControl = await SiteConditionControlFactory.persist(
        db_session,
        site_condition_hazard_id=hazard.id,
    )
    await db_session.refresh(site_condition)
    await db_session.refresh(hazard)

    variables = {"siteCondition": {"id": site_condition.id, "hazards": []}}

    data = await execute_gql(**edit_site_condition_mutation, variables=variables)
    assert data["siteCondition"]["id"] == str(site_condition.id)
    assert len(data["siteCondition"]["hazards"]) == 0

    await db_session.refresh(hazard)
    await db_session.refresh(control)
    assert_recent_datetime(hazard.archived_at)
    assert_recent_datetime(control.archived_at)

    og_hazard_archived_at = hazard.archived_at
    og_control_archived_at = control.archived_at

    # archive again
    data = await execute_gql(**edit_site_condition_mutation, variables=variables)
    assert data["siteCondition"]["id"] == str(site_condition.id)

    await db_session.refresh(hazard)
    await db_session.refresh(control)

    assert og_hazard_archived_at == hazard.archived_at
    assert og_control_archived_at == control.archived_at


@pytest.mark.asyncio
@pytest.mark.integration
async def test_edit_evaluated_site_condition(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    We shouldn't allow to edit a evaluated site condition
    """
    site_condition: SiteCondition = await SiteConditionFactory.persist_evaluated(
        db_session
    )

    response = await execute_gql(
        **edit_site_condition_mutation,
        variables={"siteCondition": {"id": site_condition.id, "hazards": []}},
        raw=True,
    )
    assert response.json().get("errors")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_site_condition_unique_library_per_location(
    db_session: AsyncSession,
    async_sessionmaker: sessionmaker,
) -> None:
    """
    Make sure we don't have duplicated library site condition for same project location
    """

    user_id: uuid.UUID = (await UserFactory.persist(db_session)).id
    location_id: uuid.UUID = (await LocationFactory.persist(db_session)).id
    library_id: uuid.UUID = (await LibrarySiteConditionFactory.persist(db_session)).id

    # archived site condition should be ignored
    await SiteConditionFactory.persist(
        db_session,
        location_id=location_id,
        library_site_condition_id=library_id,
        archived_at=datetime.utcnow(),
    )
    # not-manual site condition should be ignored
    await SiteConditionFactory.persist_evaluated(
        db_session,
        location_id=location_id,
        library_site_condition_id=library_id,
    )

    failed = []

    async def test_create(index: int) -> None:
        session: AsyncSession = async_sessionmaker()
        async with session as session_with_close:
            user_manager = UserManager(session_with_close)
            library_manager = LibraryManager(session_with_close)
            library_site_condition_manager = LibrarySiteConditionManager(db_session)
            sc_manager = SiteConditionManager(
                session_with_close, library_manager, library_site_condition_manager
            )

            user = (await user_manager.get_users(ids=[user_id]))[0]
            try:
                await sc_manager.create_site_condition(
                    SiteConditionCreate(
                        location_id=location_id,
                        library_site_condition_id=library_id,
                        is_manually_added=True,
                    ),
                    hazards=[],
                    user=user,
                )
            except ValueError:
                failed.append(index)

    await asyncio.gather(*(test_create(index) for index in range(5)))

    items = (
        await db_session.exec(
            select(SiteCondition)
            .where(SiteCondition.location_id == location_id)
            .where(SiteCondition.library_site_condition_id == library_id)
            .where(col(SiteCondition.is_manually_added).is_(True))
            .where(col(SiteCondition.archived_at).is_(None))
        )
    ).all()
    # Only one should be added
    assert len(items) == 1
    assert len(failed) == 4


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_evaluated_site_condition(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    We shouldn't allow to delete a evaluated site condition
    """
    site_condition: SiteCondition = await SiteConditionFactory.persist_evaluated(
        db_session
    )

    delete_site_condition_mutation = {
        "operation_name": "DeleteSiteCondition",
        "query": "mutation DeleteSiteCondition($id: UUID!) { siteCondition: deleteSiteCondition(id: $id) }",
    }
    response = await execute_gql(
        **delete_site_condition_mutation, variables={"id": site_condition.id}, raw=True
    )
    assert response.json().get("errors")
