import uuid
from typing import Optional

from sqlmodel import col, select

from worker_safety_service.models import AsyncSession, LibraryTask, set_order_by
from worker_safety_service.models.ingest import Element, ElementLibraryTaskLink
from worker_safety_service.types import OrderBy


class ElementManager:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_element_by_name(self, element_name: str) -> Optional[Element]:
        statement = select(Element).where(Element.name == element_name)
        return (await self.session.exec(statement)).first()

    async def get_elements(
        self,
        ids: list[uuid.UUID] | None = None,
        order_by: list[OrderBy] | None = None,
    ) -> list[Element]:
        """
        Retrieve elements
        """
        if ids is not None and not ids:
            return []

        statement = select(Element)
        if ids:
            statement = statement.where(col(Element.id).in_(ids))

        statement = set_order_by(Element, statement, order_by=order_by)
        return (await self.session.exec(statement)).all()

    async def get_elements_by_id(
        self, ids: list[uuid.UUID]
    ) -> dict[uuid.UUID, Element]:
        return {i.id: i for i in await self.get_elements(ids=ids)}

    async def get_associated_library_tasks(self, element_id: str) -> list[LibraryTask]:
        statement = (
            select(LibraryTask)
            .join(ElementLibraryTaskLink)
            .where(ElementLibraryTaskLink.element_id == element_id)
        )

        return (await self.session.exec(statement)).all()

    async def create_element(self, name: str) -> Element:
        element = Element(name=name)

        self.session.add(element)
        await self.session.commit()

        return element
