import io

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse

from worker_safety_service.dal.data_source import DataSourceManager
from worker_safety_service.enums import FileType
from worker_safety_service.keycloak import authenticate_user, get_user
from worker_safety_service.models import User
from worker_safety_service.models.data_source import (
    DataSourceCreate,
    DataSourceResponse,
)
from worker_safety_service.rest.dependency_injection.managers import (
    get_data_source_manager,
)
from worker_safety_service.urbint_logging import get_logger
from worker_safety_service.utils import parse_file

logger = get_logger(__name__)

router = APIRouter(dependencies=[Depends(authenticate_user)])


@router.get(
    "/uploads/data-sources/", response_model=list[DataSourceResponse], tags=["Uploads"]
)
async def get_data_sources(
    user: User = Depends(get_user),
    data_source_manager: DataSourceManager = Depends(get_data_source_manager),
) -> list[DataSourceResponse]:
    """
    Get all data sources for the authenticated user's tenant.
    """
    db_results = await data_source_manager.get_all(user.tenant_id)
    data_sources = [
        DataSourceResponse(
            id=ds.id,
            name=ds.name,
            created_by_id=ds.created_by_id,
            created_by_username=created_by_user.get_name(),
            tenant_id=ds.tenant_id,
            archived_at=ds.archived_at,
            columns=list(ds.raw_json.keys()) if ds.raw_json else [],
            file_name=ds.file_name,
            file_type=ds.file_type,
            created_at=ds.created_at,
            updated_at=ds.updated_at,
        )
        for ds, created_by_user in db_results
    ]
    return data_sources


@router.get(
    "/uploads/data-sources/{data_source_id}/columns/{column_name}", tags=["Uploads"]
)
async def get_column_data(
    data_source_id: str,
    column_name: str,
    user: User = Depends(get_user),
    data_source_manager: DataSourceManager = Depends(get_data_source_manager),
) -> JSONResponse:
    """
    Get all values for a specific column in a data source.
    """
    column_data = await data_source_manager.get_column_data(
        data_source_id, column_name, user.tenant_id
    )
    if column_data is None:
        raise HTTPException(status_code=404, detail="Data source or column not found")

    return JSONResponse(
        status_code=200,
        content={
            "data_source_id": data_source_id,
            "column_name": column_name,
            "values": column_data,
            "count": len(column_data),
        },
    )


@router.get("/uploads/data-sources/{data_source_id}/download", tags=["Uploads"])
async def download_data_source(
    data_source_id: str,
    user: User = Depends(get_user),
    data_source_manager: DataSourceManager = Depends(get_data_source_manager),
) -> StreamingResponse:
    """
    Download the original file for a data source.
    """
    data_source = await data_source_manager.get_data_source_by_id(
        data_source_id, user.tenant_id
    )
    if not data_source:
        raise HTTPException(status_code=404, detail="Data source not found")

    if not data_source.original_file_content:
        raise HTTPException(
            status_code=404, detail="Original file content not available"
        )

    # Determine content type based on file type
    content_type_map = {
        ".csv": "text/csv",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".xls": "application/vnd.ms-excel",
        ".xlsm": "application/vnd.ms-excel.sheet.macroEnabled.12",
    }
    content_type = content_type_map.get(
        data_source.file_type.lower(), "application/octet-stream"
    )

    return StreamingResponse(
        io.BytesIO(data_source.original_file_content),
        media_type=content_type,
        headers={
            "Content-Disposition": f"attachment; filename={data_source.file_name}"
        },
    )


@router.post("/uploads/data-sources/", tags=["Uploads"])
async def create_data_source(
    file: UploadFile,
    data_source_name: str | None = Form(None),
    user: User = Depends(get_user),
    data_source_manager: DataSourceManager = Depends(get_data_source_manager),
) -> JSONResponse:
    """
    Upload and parse a CSV or Excel file to create a data source.
    """
    if not file.filename:
        return JSONResponse(
            status_code=400,
            content={"detail": "File must have a valid filename"},
        )

    # Store filename in a variable after validation
    filename = file.filename
    file_ext = filename.split(".")[-1] if "." in filename else ""
    file_type: FileType | None = None
    try:
        file_type = FileType.from_string(file_ext)
    except ValueError as e:
        logger.error(f"Unsupported file format: {filename}: {str(e)}")
        return JSONResponse(
            status_code=400,
            content={"detail": f"Unsupported file format: {filename}"},
        )

    if data_source_name is None:
        data_source_name = filename.split(".")[0] if "." in filename else filename

    # Read file content
    file_content = await file.read()

    # Parse file based on type
    try:
        json_result = parse_file(file_content, file_type)
    except ValueError as e:
        logger.error(f"Error parsing file {filename}: {str(e)}")
        return JSONResponse(
            status_code=400,
            content={"detail": "An unexpected error occurred while parsing the file."},
        )
    except Exception as e:
        logger.error(f"Error parsing file {filename}: {str(e)}")
        return JSONResponse(
            status_code=400,
            content={"detail": "An unexpected error occurred while parsing the file."},
        )

    data_source = DataSourceCreate(
        name=str(data_source_name).strip(),
        raw_json=json_result,
        file_name=filename,
        original_file_content=file_content,
        file_type=file_type.value,
    )

    try:
        result_data_source = await data_source_manager.create(data_source, user)
        if not result_data_source:
            return JSONResponse(
                status_code=500,
                content={"detail": "Failed to create data source. Check logs"},
            )

        return JSONResponse(
            status_code=200,
            content={
                "message": f"Data source '{data_source_name}' created or updated successfully from file '{filename}'.",
                "data_source_id": str(result_data_source.id),
                "columns": list(json_result.keys()),
                "file_type": file_type.value,
            },
        )
    except Exception as e:
        logger.exception(f"Error creating data source: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "detail": "An unexpected error occurred while creating the data source."
            },
        )
