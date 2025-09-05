import asyncio
import io
import os
import time
from datetime import datetime
from typing import IO, Any, Optional
from uuid import UUID
from zoneinfo import ZoneInfo

import phonenumbers
import weasyprint  # type: ignore
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from phonenumbers import NumberParseException
from starlette.concurrency import run_in_threadpool  # Import run_in_threadpool

from ws_customizable_workflow.managers.services.cache import Cache, get_cache
from ws_customizable_workflow.managers.services.forms import FormsManager
from ws_customizable_workflow.middlewares import (
    get_user,
    is_user_password,
    set_database,
)
from ws_customizable_workflow.models.base import FormStatus
from ws_customizable_workflow.models.form_models import Form
from ws_customizable_workflow.models.users import UserBase
from ws_customizable_workflow.urbint_logging import get_logger
from ws_customizable_workflow.utils.oauth2 import password_scheme

logger = get_logger(__name__)

pdf_download_router = APIRouter(
    prefix="/pdf_download",
    tags=["PDFDOWNLOAD"],
    dependencies=[
        Depends(set_database),
        Depends(password_scheme),
        Depends(is_user_password),
    ],
)


def format_phone_with_library(number: str, country_code: str = "US") -> str:
    """
    Format a phone number using the phonenumbers library.
    """
    try:
        parsed_number = phonenumbers.parse(str(number), country_code)
        formatted = phonenumbers.format_number(
            parsed_number, phonenumbers.PhoneNumberFormat.NATIONAL
        )
        return formatted
    except NumberParseException:
        return "Invalid phone number"


def format_phone_numbers_in_form_data(form_data: Any) -> Any:
    """
    Recursively find and format phone numbers in form data structure.
    """
    if isinstance(form_data, dict):
        # Check if this is an input_phone_number element
        if form_data.get("type") == "input_phone_number" and "properties" in form_data:
            properties = form_data["properties"]
            if "user_value" in properties and properties["user_value"]:
                properties["user_value"] = format_phone_with_library(
                    properties["user_value"]
                )
        return {
            key: format_phone_numbers_in_form_data(value)
            for key, value in form_data.items()
        }
    elif isinstance(form_data, list):
        return [format_phone_numbers_in_form_data(item) for item in form_data]
    else:
        return form_data


def datetimeformat(value: Any, format: str = "%b %d, %Y, %I:%M %p") -> str:
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.strftime(format)
    if isinstance(value, str):
        try:
            dt = datetime.fromisoformat(value)
        except ValueError:
            try:
                dt = datetime.strptime(value, "%Y-%m-%dT%H:%M")
            except ValueError:
                return value
        return dt.strftime(format)
    return str(value)


PDF_TEMPLATE_DIR = "ws_customizable_workflow/managers/pdf_download_templates"
PDF_TEMPLATE_FILE_NAME = "cwf_template_form.html.jinja"
PDF_TIMEOUT_SECONDS = 300  # Default timeout set for 5 mins


# Initialize Jinja2Templates
jinja_templates = Jinja2Templates(directory=PDF_TEMPLATE_DIR)
jinja_templates.env.filters["datetimeformat"] = datetimeformat


async def generate_pdf_content(html_content: str) -> IO[bytes]:
    """
    Helper function to generate PDF content using WeasyPrint within a threadpool.
    This is crucial for preventing blocking the main FastAPI event loop.
    """
    start_time = time.time()

    logger.debug(
        "Starting PDF generation",
        html_length=len(html_content),
        workflow="pdf_download",
    )

    def _generate() -> IO[bytes]:  # Define an inner function
        buffer = io.BytesIO()
        weasyprint.HTML(string=html_content).write_pdf(buffer)
        buffer.seek(0)
        return buffer

    try:
        # Await the result of run_in_threadpool
        result = await run_in_threadpool(func=_generate)

        duration_ms = (time.time() - start_time) * 1000

        logger.debug(
            "PDF generation completed",
            workflow="pdf_download",
            duration_ms=duration_ms,
        )

        return result

    except Exception as exc:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(
            "PDF generation failed",
            error=str(exc),
            duration_ms=duration_ms,
            workflow="pdf_download",
            exc_info=True,
        )
        raise


@pdf_download_router.get("/forms/{form_id}")
async def forms_pdf_download(
    form_id: UUID,
    request: Request,
    user_details: UserBase = Depends(get_user),
    cache: Cache = Depends(get_cache),
    timezone: Optional[str] = None,
) -> StreamingResponse:
    """
    Endpoint to download a completed CWF form as a PDF
    """
    logger.info("PDF download requested", workflow="pdf_download", form_id=str(form_id))
    try:
        # Enforce timeout for the entire operation
        response = await asyncio.wait_for(
            _forms_pdf_download_logic(form_id, user_details, cache, request, timezone),
            timeout=PDF_TIMEOUT_SECONDS,
        )

        logger.info(
            "PDF download completed successfully",
            workflow="pdf_download",
            form_id=str(form_id),
        )
        return response

    except asyncio.TimeoutError:
        logger.error(
            "PDF download timed out",
            workflow="pdf_download",
            form_id=str(form_id),
            timeout_seconds=PDF_TIMEOUT_SECONDS,
        )
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="The request timed out. Please try again later.",
        )
    except HTTPException as e:
        logger.warning(
            "PDF download failed with HTTP exception",
            workflow="pdf_download",
            form_id=str(form_id),
            status_code=e.status_code,
            detail=e.detail,
        )
        raise e  # Re-raise HTTPException with its original status code
    except FileNotFoundError as e:
        logger.error(
            "PDF template file not found",
            workflow="pdf_download",
            form_id=str(form_id),
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Template file not found: {e}",
        )
    except Exception as e:
        logger.error(
            "Unexpected error during PDF download",
            workflow="pdf_download",
            form_id=str(form_id),
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {e}",
        )


async def _forms_pdf_download_logic(
    form_id: UUID,
    user_details: UserBase,
    cache: Cache,
    request: Request,
    timezone: Optional[str] = None,
) -> StreamingResponse:
    """
    Logic for the forms_pdf_download endpoint, extracted for timeout handling.
    """
    logger.debug(
        "Starting PDF download logic", workflow="pdf_download", form_id=str(form_id)
    )

    # Validate template file existence
    template_path = os.path.join(PDF_TEMPLATE_DIR, PDF_TEMPLATE_FILE_NAME)
    if not os.path.exists(template_path):
        logger.error(
            "PDF template file does not exist",
            workflow="pdf_download",
            template_path=template_path,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Template file '{PDF_TEMPLATE_FILE_NAME}' does not exist.",
        )

    # Load the template
    template_load_start = time.time()
    try:
        template = jinja_templates.get_template(PDF_TEMPLATE_FILE_NAME)

        template_load_duration = (time.time() - template_load_start) * 1000
        logger.debug(
            "PDF template loaded successfully",
            workflow="pdf_download",
            template_name=PDF_TEMPLATE_FILE_NAME,
            load_duration_ms=template_load_duration,
        )
    except Exception as exc:
        template_load_duration = (time.time() - template_load_start) * 1000

        logger.error(
            "Failed to load PDF template",
            workflow="pdf_download",
            template_name=PDF_TEMPLATE_FILE_NAME,
            error=str(exc),
            load_duration_ms=template_load_duration,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load PDF template",
        )

    # Fetch form data
    form_fetch_start = time.time()
    try:
        form_data: Form | None = await FormsManager.get_form_by_id(form_id, cache)
        # No need to check for not form_data or is_archived or call ExceptionHandler again

        if not form_data:
            form_fetch_duration = (time.time() - form_fetch_start) * 1000
            logger.warning(
                "Form not found for PDF download",
                workflow="pdf_download",
                form_id=str(form_id),
                exists=form_data is not None,
                fetch_duration_ms=form_fetch_duration,
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Form with id '{form_id}' not found.",
            )

        form_fetch_duration = (time.time() - form_fetch_start) * 1000

        logger.debug(
            "Form data retrieved for PDF",
            workflow="pdf_download",
            form_id=str(form_id),
            form_title=form_data.properties.title if form_data.properties else None,
            form_status=form_data.properties.status if form_data.properties else None,
            fetch_duration_ms=form_fetch_duration,
        )

    except Exception as exc:
        form_fetch_duration = (time.time() - form_fetch_start) * 1000

        logger.error(
            "Failed to retrieve form data for PDF",
            workflow="pdf_download",
            form_id=str(form_id),
            error=str(exc),
            fetch_duration_ms=form_fetch_duration,
            exc_info=True,
        )
        raise

    # Validate form status
    template_name = form_data.properties.title
    form_status = form_data.properties.status
    if form_status != FormStatus.COMPLETE:
        logger.warning(
            "Attempted PDF download of incomplete form",
            workflow="pdf_download",
            form_id=str(form_id),
            form_status=form_status,
            template_name=template_name,
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"The form '{template_name}' is not in a completed state and cannot be exported as a PDF.",
        )

    # Prepare data for rendering
    last_updated_at = form_data.updated_at
    report_date: datetime | None = form_data.properties.report_start_date

    if timezone and form_data.updated_at:
        try:
            client_tz = ZoneInfo(timezone)
            if form_data.updated_at.tzinfo is None:
                updated_at_utc = form_data.updated_at.replace(tzinfo=ZoneInfo("UTC"))
            else:
                updated_at_utc = form_data.updated_at

            form_data.updated_at = updated_at_utc.astimezone(client_tz)
            last_updated_at = form_data.updated_at

            logger.debug(
                "Converted form_data.updated_at to client timezone",
                workflow="pdf_download",
                form_id=str(form_id),
                client_timezone=timezone,
                converted_time=form_data.updated_at.isoformat(),
            )
        except Exception as exc:
            logger.warning(
                "Failed to convert timezone, using original time",
                workflow="pdf_download",
                form_id=str(form_id),
                client_timezone=timezone,
                error=str(exc),
            )

    file_name_date = (
        report_date or form_data.updated_at or form_data.completed_at or datetime.now()
    )
    # Format phone numbers in the form data
    # Convert Pydantic model to dict, format phone numbers, then convert back
    form_dict = form_data.dict()
    formatted_form_dict = format_phone_numbers_in_form_data(form_dict)

    # Create a new Form object from the formatted dictionary
    from ws_customizable_workflow.models.form_models import Form

    form_data = Form(**formatted_form_dict)
    render_start = time.time()
    try:
        html_content = template.render(
            form_data=form_data,
            template_name=template_name,
            status=form_status.value,
            render_summary_block=False,
            render_form_block=True,
            last_updated_at=last_updated_at,
        )

        render_duration = (time.time() - render_start) * 1000

        logger.debug(
            "HTML content rendered for PDF",
            workflow="pdf_download",
            form_id=str(form_id),
            html_length=len(html_content),
            render_duration_ms=render_duration,
        )

    except Exception as exc:
        render_duration = (time.time() - render_start) * 1000

        logger.error(
            "Failed to render HTML template for PDF",
            workflow="pdf_download",
            form_id=str(form_id),
            error=str(exc),
            render_duration_ms=render_duration,
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to render PDF template",
        )

    # Generate PDF in a non-blocking manner
    pdf_content = await generate_pdf_content(html_content)

    # Prepare response
    user_email = form_data.updated_by.email if form_data.updated_by else "unknown"
    pdf_filename = f"{template_name} Export - Urbint - [{user_email}] - {file_name_date.strftime('%m-%d-%y')}.pdf"

    headers = {
        "Content-Disposition": f'attachment; filename="{pdf_filename}"',
        "Content-Type": "application/pdf",
        "Access-Control-Expose-Headers": "Content-Disposition",
    }

    logger.info(
        "PDF response prepared",
        workflow="pdf_download",
        form_id=str(form_id),
        filename=pdf_filename,
    )

    return StreamingResponse(pdf_content, headers=headers, media_type="application/pdf")
