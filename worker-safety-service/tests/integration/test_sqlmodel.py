import asyncio
import uuid

import pytest
from pydantic import ValidationError, validator
from sqlmodel import Field, select

from worker_safety_service.models import AsyncSession, SQLModel, Tenant


@pytest.mark.asyncio
@pytest.mark.integration
async def test_no_pydantic_raise_on_table() -> None:
    """SQLModel don't validate table classes"""

    class TestTable(SQLModel, table=True):
        __tablename__ = "some_test_table"

        id: uuid.UUID = Field(
            default_factory=uuid.uuid4, primary_key=True, nullable=False
        )
        name: str

        @validator("name")
        def check_name(cls, v: str) -> str:  # type: ignore
            assert False, "Always raise error"

    # No validation raised
    obj = TestTable(name=object())
    assert obj.name is None
    obj = TestTable(name="some name")
    assert obj.name is None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_pydantic_raise_on_base_model() -> None:
    """SQLModel only validate base classes (without table=True)"""

    class TestTableBase(SQLModel):
        id: uuid.UUID = Field(
            default_factory=uuid.uuid4, primary_key=True, nullable=False
        )
        name: str

        @validator("name")
        def check_name(cls, v: str) -> str:  # type: ignore
            assert False, "Always raise error"

    class TestTable(TestTableBase, table=True):
        __tablename__ = "some_test_table_2"

    # No validation raised
    obj = TestTable(name=object())
    assert obj.name is None
    obj = TestTable(name="some name")
    assert obj.name is None

    # Validation raised
    with pytest.raises(ValidationError):
        obj = TestTableBase(name=object())
    with pytest.raises(ValidationError):
        obj = TestTableBase(name="some name")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_pydantic_dont_validate_model_updates() -> None:
    """SQLModel don't validate obj attribute set"""

    class TestTableBase(SQLModel):
        id: uuid.UUID = Field(
            default_factory=uuid.uuid4, primary_key=True, nullable=False
        )
        name: str

        @validator("name")
        def check_name(cls, v: str) -> str:  # type: ignore
            assert v == "valid", "Must be valid"
            return v

    class TestTable(TestTableBase, table=True):
        __tablename__ = "some_test_table_3"

    # Valid
    obj = TestTable(name="valid")
    assert obj.name == "valid"

    # Update will not make pydantic validation
    obj.name = "invalid"
    assert obj.name == "invalid"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_async_db_session(db_session: AsyncSession) -> None:
    """
    With AsyncSession it's already without transaction and we could make multiple queries at same time
    """

    name = uuid.uuid4().hex
    name_2 = uuid.uuid4().hex
    db_session.add_all(
        [
            Tenant(tenant_name=name, auth_realm_name=name, display_name=name),
            Tenant(tenant_name=name_2, auth_realm_name=name_2, display_name=name_2),
        ]
    )
    await db_session.flush()

    statement = select(Tenant).where(Tenant.tenant_name == name)
    statement_2 = select(Tenant).where(Tenant.tenant_name == name_2)
    tenant_scalar, tenant_2_scalar = await asyncio.gather(
        db_session.exec(statement),
        db_session.exec(statement_2),
    )
    tenant = tenant_scalar.first()
    assert tenant
    assert tenant.tenant_name == name
    tenant_2 = tenant_2_scalar.first()
    assert tenant_2
    assert tenant_2.tenant_name == name_2
