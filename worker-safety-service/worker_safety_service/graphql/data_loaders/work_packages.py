import datetime
import functools
import uuid
from typing import Optional, Sequence

from strawberry.dataloader import DataLoader

from worker_safety_service.dal.locations import LocationsManager
from worker_safety_service.dal.work_packages import WorkPackageManager
from worker_safety_service.exceptions import ResourceReferenceException, TenantException
from worker_safety_service.graphql.data_loaders.utils import create_order_by_hash
from worker_safety_service.models import ProjectStatus, User
from worker_safety_service.models.base import Location, LocationEdit
from worker_safety_service.models.work_packages import (
    WorkPackage,
    WorkPackageCreate,
    WorkPackageEdit,
)
from worker_safety_service.risk_model.riskmodelreactor import RiskModelReactorInterface
from worker_safety_service.risk_model.triggers import ProjectChanged
from worker_safety_service.types import OrderBy


class TenantWorkPackageLoader:
    """
    Given project ids, load objects
    """

    def __init__(
        self,
        work_package_manager: WorkPackageManager,
        risk_model_reactor: RiskModelReactorInterface,
        locations_manager: LocationsManager,
        tenant_id: uuid.UUID,
    ):
        """
        Takes a tenant that restricts all queries to only work on a specific
        tenant
        """
        self.tenant_id = tenant_id
        self.__manager = work_package_manager
        self.__risk_model_reactor = risk_model_reactor

        self.me = DataLoader(load_fn=self.load_projects)
        self.with_archived = DataLoader(load_fn=self.load_projects_with_archived)
        self.__locations_map: dict[int | None, DataLoader] = {}
        self.minimum_task_date = DataLoader(load_fn=self.load_minimum_task_dates)
        self.maximum_task_date = DataLoader(load_fn=self.load_maximum_task_dates)
        self.__locations_manager = locations_manager

    async def load_projects(
        self, project_ids: list[uuid.UUID]
    ) -> list[WorkPackage | None]:
        items = await self.__manager.get_projects_by_id(
            project_ids, tenant_id=self.tenant_id
        )
        return [items.get(i) for i in project_ids]

    async def load_projects_with_archived(
        self, project_ids: list[uuid.UUID]
    ) -> list[WorkPackage | None]:
        items = await self.__manager.get_projects_by_id(
            project_ids, tenant_id=self.tenant_id, with_archived=True
        )
        return [items.get(i) for i in project_ids]

    def locations(
        self,
        order_by: list[OrderBy] | None = None,
    ) -> DataLoader:
        key = create_order_by_hash(order_by)
        dataloader = self.__locations_map.get(key)
        if not dataloader:
            dataloader = self.__locations_map[key] = DataLoader(
                load_fn=functools.partial(
                    self.load_project_locations, order_by=order_by
                )
            )
        return dataloader

    async def load_project_locations(
        self,
        project_ids: list[uuid.UUID],
        order_by: list[OrderBy] | None = None,
        load_projects: bool = True,
    ) -> list[list[Location]]:
        """
        Loads project_locations by project_id. Excludes archived locations.
        """

        final: dict[uuid.UUID, list[Location]] = {i: [] for i in project_ids}
        for location in await self.__locations_manager.get_locations(
            project_ids=project_ids,
            order_by=order_by,
            tenant_id=self.tenant_id,
            load_project=load_projects,
        ):
            if location.project_id is None:
                raise RuntimeError(
                    f"Unexpected location {location.id} without a project_id"
                )
            final[location.project_id].append(location)
        return list(final.values())

    async def load_minimum_task_dates(
        self, project_ids: list[uuid.UUID]
    ) -> list[datetime.date | None]:
        items = await self.__manager.get_minimum_task_start_date_for_projects(
            project_ids
        )
        return [items.get(i) for i in project_ids]

    async def load_maximum_task_dates(
        self, project_ids: list[uuid.UUID]
    ) -> list[datetime.date | None]:
        items = await self.__manager.get_maximum_task_end_date_for_projects(project_ids)
        return [items.get(i) for i in project_ids]

    async def get_projects(
        self,
        search: str | None = None,
        risk_level_date: datetime.date | None = None,
        status: ProjectStatus | None = None,
        order_by: list[OrderBy] | None = None,
        external_keys: list[str] | None = None,
        after: uuid.UUID | None = None,
        limit: int | None = None,
        use_seek_pagination: bool | None = False,
    ) -> list[WorkPackage]:
        return await self.__manager.get_projects(
            status=status,
            search=search,
            tenant_id=self.tenant_id,
            risk_level_date=risk_level_date,
            order_by=order_by,
            external_keys=external_keys,
            after=after,
            limit=limit,
            use_seek_pagination=use_seek_pagination,
        )

    async def get_projects_with_risk(
        self,
        search: str | None = None,
        risk_level_date: datetime.date | None = None,
        status: ProjectStatus | None = None,
        order_by: list[OrderBy] | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> tuple[bool, list[tuple[WorkPackage, str] | list[WorkPackage]]]:
        return await self.__manager.get_projects_with_risk(
            status=status,
            search=search,
            tenant_id=self.tenant_id,
            risk_level_date=risk_level_date,
            order_by=order_by,
            limit=limit,
            offset=offset,
        )

    async def get_work_package_by_location(
        self,
        location_id: uuid.UUID,
    ) -> WorkPackage | None:
        return await self.__manager.get_work_package_by_location(
            location_id,
            tenant_id=self.tenant_id,
        )

    async def create_work_packages(
        self,
        projects: list[WorkPackageCreate],
        user: Optional[User] = None,
    ) -> Sequence[WorkPackage]:
        # Make sure that projects are created in current tenant
        for project in projects:
            if not project.tenant_id == self.tenant_id:
                raise TenantException(
                    "It is not possible to create projects in another tenant"
                )
        created_work_packages = await self.__manager.create_work_packages(
            projects, user
        )

        # Will trigger the recalculation of the supervisors for these projects
        for wp in created_work_packages:
            await self.__risk_model_reactor.add(ProjectChanged(wp.id))

        return created_work_packages

    async def edit_project_with_locations(
        self,
        db_project: WorkPackage,
        project: WorkPackageEdit,
        locations: list[LocationEdit] | None,
        user: User | None,
    ) -> None:
        # Make sure that project is created in current tenant
        if not db_project.tenant_id == self.tenant_id:
            raise TenantException(
                "It is not possible to update projects in another tenant"
            )

        await self.__manager.edit_project_with_locations(
            db_project,
            project,
            locations,
            user,
        )

        # TODO: I had to trigger everything because I have no way of knowing the ids of newly created locations.
        # TODO: There is also no guarantee that the contractor was changed.
        await self.__risk_model_reactor.add(ProjectChanged(db_project.id))

    async def update_work_package(
        self,
        edited_work_package: WorkPackageEdit,
        id: uuid.UUID,
        user: User | None = None,
    ) -> WorkPackage | None:
        db_work_package = await self.load_projects(project_ids=[id])
        if not db_work_package:
            raise ResourceReferenceException("Work package not found")
        assert db_work_package[0]
        await self.edit_project_with_locations(
            db_project=db_work_package[0],
            project=edited_work_package,
            locations=[],
            user=user,
        )
        updated_work_package = await self.load_projects(project_ids=[id])
        assert updated_work_package
        return updated_work_package[0]

    async def archive_project(
        self,
        db_project: WorkPackage,
        user: User | None = None,
    ) -> None:
        await self.__manager.archive_project(db_project.id, user)
        await self.__risk_model_reactor.add(ProjectChanged(db_project.id))

    async def archive_all_tenant_projects(
        self, tenant_id: uuid.UUID, user: User
    ) -> int:
        return await self.__manager.archive_all_tenant_projects(
            tenant_id=tenant_id, user=user
        )
