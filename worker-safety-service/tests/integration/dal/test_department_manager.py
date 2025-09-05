import pytest

from tests.factories import OpcoFactory
from worker_safety_service.dal.department_manager import DepartmentManager
from worker_safety_service.models import AsyncSession, DepartmentCreate
from worker_safety_service.urbint_logging import get_logger

logger = get_logger(__name__)


# Successfully creating an insight
@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_department(db_session: AsyncSession) -> None:
    opco = await OpcoFactory.persist(db_session)
    department_manager = DepartmentManager(db_session)

    departments = await department_manager.get_all_departments(opco_id=opco.id)
    assert len(departments) == 0

    new_department = await department_manager.create_department(
        DepartmentCreate(name="department_1", opco_id=opco.id)
    )
    assert new_department
    assert new_department.name == "department_1"

    departments = await department_manager.get_all_departments(opco_id=opco.id)
    assert len(departments) == 1

    new_department = await department_manager.create_department(
        DepartmentCreate(name="department_2", opco_id=opco.id)
    )
    assert new_department
    assert new_department.name == "department_2"

    departments = await department_manager.get_all_departments(opco_id=opco.id)
    assert len(departments) == 2


# Update Department
@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_department(db_session: AsyncSession) -> None:
    opco = await OpcoFactory.persist(db_session)
    department_manager = DepartmentManager(db_session)

    department = await department_manager.create_department(
        DepartmentCreate(name="department_1", opco_id=opco.id)
    )

    departments = await department_manager.get_all_departments(opco_id=opco.id)
    assert departments[0].name == department.name

    department.name = "department_1_updated"
    await department_manager.edit_department(department=department)

    departments = await department_manager.get_all_departments(opco_id=opco.id)
    assert departments[0].name == department.name


# Delete department
@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_department(db_session: AsyncSession) -> None:
    opco = await OpcoFactory.persist(db_session)
    department_manager = DepartmentManager(db_session)

    department = await department_manager.create_department(
        DepartmentCreate(name="department_1", opco_id=opco.id)
    )

    departments = await department_manager.get_all_departments(opco_id=opco.id)
    assert len(departments) == 1

    await department_manager.delete_department(department.id)

    departments = await department_manager.get_all_departments(opco_id=opco.id)
    assert len(departments) == 0
