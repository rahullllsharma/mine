import uuid

import pytest
from httpx import AsyncClient
from mongomock_motor import AsyncMongoMockClient

from tests.factories.form_factory import FormFactory
from ws_customizable_workflow.managers.DBCRUD.dbcrud import CRUD
from ws_customizable_workflow.models.form_models import Form
from ws_customizable_workflow.models.template_models import Template

templates_crud_manager = CRUD(Template)


@pytest.mark.asyncio
async def test_forms_v2_create(
    app_client: AsyncClient,
    db_client: AsyncMongoMockClient,
) -> None:
    # Arrange
    form: Form = FormFactory.build()
    form.properties.title = "Test Form Create"
    form_data = form.model_dump(mode="json")

    # Act
    response = await app_client.put(f"/v2/forms/{form.id}", json=form_data)
    db_form = await Form.get(form.id)

    # Assert
    assert response.status_code == 201, response.json()
    assert form_data == response.json()
    assert db_form is not None
    assert (
        db_form.model_dump(mode="json")["properties"]["title"] == form.properties.title
    )


@pytest.mark.asyncio
async def test_forms_v2_update(
    app_client: AsyncClient,
    db_client: AsyncMongoMockClient,
) -> None:
    # Arrange
    form: Form = FormFactory.build()
    await form.save()
    form.properties.title = "Test Form Create"
    form_data = form.model_dump(mode="json")

    # Act
    response = await app_client.put(f"/v2/forms/{form.id}", json=form_data)
    db_form = await Form.get(form.id)

    # Assert
    assert response.status_code == 200, response.json()
    assert form_data == response.json()
    assert db_form is not None
    assert (
        db_form.model_dump(mode="json")["properties"]["title"] == form.properties.title
    )


@pytest.mark.asyncio
async def test_forms_v2_invalid_id(
    app_client: AsyncClient,
    db_client: AsyncMongoMockClient,
) -> None:
    # Arrange
    form: Form = FormFactory.build()
    form_data = form.model_dump(mode="json")

    # Act
    response = await app_client.put(f"/v2/forms/{uuid.uuid4()}", json=form_data)

    # Assert
    assert response.status_code == 400, response.json()
