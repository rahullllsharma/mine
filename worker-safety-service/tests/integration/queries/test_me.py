#!/usr/bin/env python3

from typing import Any

import pytest

from tests.db_data import DBData
from tests.factories import (
    AdminUserFactory,
    DepartmentFactory,
    ManagerUserFactory,
    OpcoFactory,
    SupervisorUserFactory,
    ViewerUserFactory,
)
from tests.integration.conftest import ExecuteGQL
from worker_safety_service.models import AsyncSession, User

query_me = """
query TestQuery ($withTenant: Boolean! = false, $withOpco: Boolean! = false) {
  me {
    id
    firstName
    lastName
    email
    name
    role
    tenantName
    tenant @include(if: $withTenant) {
      name
      configurations {
        entities {
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
            visible
            required
            filterable
            mappings
          }
        }
      }
    }
    opco @include(if: $withOpco) {
      id
      name
      parentOpco {
        id
        name
      }
      departments {
        id
        name
      }
    }
  }
}
"""


@pytest.mark.parametrize(
    "user_factory, role",
    [
        (AdminUserFactory, "administrator"),
        (ManagerUserFactory, "manager"),
        (SupervisorUserFactory, "supervisor"),
        (ViewerUserFactory, "viewer"),
    ],
)
@pytest.mark.asyncio
@pytest.mark.integration
async def test_query_me(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    user_factory: Any,
    role: str,
    db_data: DBData,
) -> None:
    """Query for `me` for each type of user."""
    user: User = await user_factory.persist(db_session)
    assert role == user.role

    data = await execute_gql(query=query_me, user=user)

    assert data["me"]["firstName"] == user.first_name
    assert data["me"]["lastName"] == user.last_name
    assert data["me"]["email"] == user.email
    assert data["me"]["name"] == f"{user.first_name} {user.last_name}"
    assert data["me"]["role"] == role
    assert (
        data["me"]["tenantName"] == (await db_data.tenant(user.tenant_id)).tenant_name
    )


@pytest.mark.parametrize(
    "user_factory",
    [
        AdminUserFactory,
        ManagerUserFactory,
        SupervisorUserFactory,
        ViewerUserFactory,
    ],
)
@pytest.mark.asyncio
@pytest.mark.integration
async def test_query_me_configurations(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    user_factory: Any,
) -> None:
    user = await user_factory.persist(db_session)
    data = await execute_gql(query=query_me, user=user, variables={"withTenant": True})
    assert data["me"]["tenantName"] == data["me"]["tenant"]["name"]

    # just check if configurations are OK
    assert data["me"]["tenant"]["configurations"]["entities"] is not None


@pytest.mark.parametrize(
    "user_factory",
    [
        AdminUserFactory,
        ManagerUserFactory,
        SupervisorUserFactory,
        ViewerUserFactory,
    ],
)
@pytest.mark.asyncio
@pytest.mark.integration
async def test_query_me_opcos_departments(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    user_factory: Any,
) -> None:
    parent_opco = await OpcoFactory.persist(db_session, name="National Industries")
    opco = await OpcoFactory.persist(
        db_session, name="Gas Industries", parent_id=parent_opco.id
    )
    department_1, department_2 = await DepartmentFactory.persist_many(
        db_session,
        size=2,
        per_item_kwargs=[
            {"name": "East", "opco_id": opco.id},
            {"name": "West", "opco_id": opco.id},
        ],
    )

    user = await user_factory.persist(db_session, opco_id=opco.id)
    data = await execute_gql(query=query_me, user=user, variables={"withOpco": True})

    assert data["me"]["opco"]
    assert data["me"]["opco"]["id"] == str(opco.id)
    assert data["me"]["opco"]["name"] == opco.name

    assert data["me"]["opco"]["parentOpco"]
    assert data["me"]["opco"]["parentOpco"]["id"] == str(parent_opco.id)
    assert data["me"]["opco"]["parentOpco"]["name"] == parent_opco.name

    assert data["me"]["opco"]["departments"]
    departments = data["me"]["opco"]["departments"]

    assert departments[0]["id"] == str(department_1.id)
    assert departments[0]["name"] == str(department_1.name)
    assert departments[1]["id"] == str(department_2.id)
    assert departments[1]["name"] == str(department_2.name)


@pytest.mark.parametrize(
    "user_factory",
    [
        AdminUserFactory,
        ManagerUserFactory,
        SupervisorUserFactory,
        ViewerUserFactory,
    ],
)
@pytest.mark.asyncio
@pytest.mark.integration
async def test_query_me_configurations_for_critical_activity(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    user_factory: Any,
) -> None:
    user = await user_factory.persist(db_session)
    data = await execute_gql(query=query_me, user=user, variables={"withTenant": True})
    assert data["me"]["tenantName"] == data["me"]["tenant"]["name"]

    # just check if configurations are OK
    assert data["me"]["tenant"]["configurations"]["entities"] is not None
    entities = data["me"]["tenant"]["configurations"]["entities"]
    activity_attributes_keys = []
    for entity in entities:
        if entity["key"] == "activity":
            for attribute in entity["attributes"]:
                activity_attributes_keys.append(attribute["key"])

    assert "criticalActivity" in activity_attributes_keys
