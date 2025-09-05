from fastapi import APIRouter, Depends
from pydantic import BaseModel

from worker_safety_service.dal.jsb_supervisors import JSBSupervisorsManager
from worker_safety_service.keycloak import authenticate_integration
from worker_safety_service.rest.dependency_injection.managers import (
    get_jsb_supervisor_manager,
)
from worker_safety_service.urbint_logging import get_logger
from worker_safety_service.workos.workos_data import DirectoryUsersQuery, WorkOSCrewData

router = APIRouter(
    prefix="/jsb-supervisors",
    dependencies=[Depends(authenticate_integration)],
)

logger = get_logger(__name__)


class JSBSupervisorRequestModel(BaseModel):
    perform_delete: bool = False


class JSBSupervisorsDeleteModel(BaseModel):
    message: str | None = None
    records_deleted: int
    valid_combinations: dict | None = None
    invalid_combinations: dict | None = None
    valid_combinations_count: int | None = None
    invalid_combinations_count: int | None = None


@router.delete(
    "/non-delinked",
    status_code=200,
    tags=["jsb-supervisors"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def delete_non_delinked_jsb_supervisors(
    req: JSBSupervisorRequestModel,
    jsb_supervisor_manager: JSBSupervisorsManager = Depends(get_jsb_supervisor_manager),
) -> JSBSupervisorsDeleteModel:
    """
    Need to delete all supervisors which are linked to jsbs for which the relevant crew no longer exists.
    1. Get all jsbs along with crew for which there is a record in jsb_supervisor table.
    2. Fetch the manager_ids of crews and create list of valid combinations of jsb_id and manager_id.
    3. Delete records from jsb_supervisor_link which is not part of valid combinations.
    """
    data = await jsb_supervisor_manager.get_jsb_supervisors_without_crew()
    directory_ids = set()
    for row in data:
        directory_ids.add(row["workos_directory_id"])
    #
    # WorkOS API Call to fetch all users for respective directories.
    # This is to fetch managerid using the externalid found in jsbs.contents
    workos_users = await WorkOSCrewData().fetch_workos_crew_info(
        list(directory_ids),
        DirectoryUsersQuery(
            group=None,
            limit=None,
            before=None,
            after=None,
            order=None,
        ),
        update_cache=True,
    )

    # Create a map of workos user with key as externalid/idp_id for fast fetching
    workos_users_map = {}
    if not workos_users.data:
        return JSBSupervisorsDeleteModel(
            message="No WorkOS data received.", records_deleted=0
        )

    for user in workos_users.data:
        workos_users_map.update({user.idp_id: user})

    # Calculate valid and invalid set of jsb-supervisor combinations by comparing
    # managerid received in first query and managerid received from workos
    valid_crew_jsb_map: dict = {}
    invalid_crew_jsb_map: dict = {}
    valid_combinations_count = 0
    invalid_combinations_count = 0
    for row in data:
        jsb_id = str(row["jsb_id"])
        manager_id = str(row["manager_id"])
        valid_managers = valid_crew_jsb_map.get(jsb_id, []) or []
        invalid_managers = invalid_crew_jsb_map.get(jsb_id, []) or []
        contents = row["contents"] or {}
        logger.info(f"JSB ID: {jsb_id}")
        logger.info(f"Row ManagerId: {manager_id}")
        print(f"\n\n Contents: {contents} \n\n")
        if contents and contents.get("crew_sign_off") is not None:
            for crew in contents.get("crew_sign_off", []):
                ext_id = str(crew.get("external_id"))
                wo_user = workos_users_map.get(ext_id)
                if not wo_user:
                    continue
                ws_manager_id = wo_user.custom_attributes.get("manager_id")
                logger.info(f"WS ManagerId: {ws_manager_id}")
                if manager_id == str(ws_manager_id):
                    valid_managers.append(str(ws_manager_id))
                    valid_combinations_count += 1
        valid_crew_jsb_map[jsb_id] = valid_managers
        if manager_id not in valid_managers:
            invalid_managers.append(manager_id)
            invalid_crew_jsb_map[jsb_id] = invalid_managers
            invalid_combinations_count += 1

    logger.info(f"\n Valid Combinations: {valid_crew_jsb_map} \n")
    logger.info(f"\n Invalid Combinations: {invalid_crew_jsb_map} \n")

    # Perform a delete operation for removing jsb-supervisor combinations based on
    # invalid crew map created in previous step
    del_count = 0
    if req.perform_delete:
        for jsb_id, manager_ids in invalid_crew_jsb_map.items():
            for manager_id in manager_ids:
                res = await jsb_supervisor_manager.delete_jsb_supervisors_by_jsb_id_and_manager_id(
                    jsb_id, manager_id
                )
                del_count += res
    logger.info(f"No. of deleted records: {del_count}")
    return JSBSupervisorsDeleteModel(
        records_deleted=del_count,
        valid_combinations=valid_crew_jsb_map,
        invalid_combinations=invalid_crew_jsb_map,
        valid_combinations_count=valid_combinations_count,
        invalid_combinations_count=invalid_combinations_count,
    )
