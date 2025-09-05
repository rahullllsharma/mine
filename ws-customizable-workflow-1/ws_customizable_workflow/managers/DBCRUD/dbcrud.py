import time
from typing import Any, Optional, TypeVar, Union
from uuid import UUID

from beanie import Document, SortDirection

from ws_customizable_workflow.exceptions import ExceptionHandler
from ws_customizable_workflow.models.form_models import Form
from ws_customizable_workflow.models.template_models import Template
from ws_customizable_workflow.urbint_logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T", bound=Union[type[Template], type[Form]])


class CRUD:
    def __init__(self, collection: T) -> None:
        self.collection = collection
        self.collection_name = collection.__name__.lower()

    async def get_all_documents(self) -> list[Document]:
        start_time = time.time()

        try:
            docs = await self.collection.find_all().to_list()

            duration_ms = (time.time() - start_time) * 1000
            logger.debug(
                "Retrieved all documents",
                collection=self.collection_name,
                count=len(docs),
                duration_ms=duration_ms,
            )

            return docs

        except Exception as exc:
            duration_ms = (time.time() - start_time) * 1000

            logger.error(
                "Failed to retrieve all documents",
                collection=self.collection_name,
                error=str(exc),
                duration_ms=duration_ms,
                exc_info=True,
            )
            raise

    async def create_document(self, document: Document) -> Document:
        start_time = time.time()

        try:
            result = await self.collection.create(document)

            duration_ms = (time.time() - start_time) * 1000

            logger.debug(
                "Created document",
                collection=self.collection_name,
                document_id=str(result.id) if hasattr(result, "id") else None,
                duration_ms=duration_ms,
            )

            return result

        except Exception as exc:
            duration_ms = (time.time() - start_time) * 1000

            logger.error(
                "Failed to create document",
                collection=self.collection_name,
                error=str(exc),
                duration_ms=duration_ms,
                exc_info=True,
            )
            raise

    async def get_document_by_id(self, id: UUID) -> Optional[Document]:
        start_time = time.time()

        try:
            doc = await self.collection.get(id)
            result = doc if doc else None

            duration_ms = (time.time() - start_time) * 1000

            logger.debug(
                "Retrieved document by ID",
                collection=self.collection_name,
                document_id=str(id),
                found=result is not None,
                duration_ms=duration_ms,
            )

            return result

        except Exception as exc:
            duration_ms = (time.time() - start_time) * 1000

            logger.error(
                "Failed to retrieve document by ID",
                collection=self.collection_name,
                document_id=str(id),
                error=str(exc),
                duration_ms=duration_ms,
                exc_info=True,
            )
            raise

    async def filter_documents_by_attributes(
        self,
        order_by: str = "title",
        asc: bool = True,
        skip: int = 0,
        limit: int = 10,
        **kwargs: Any,
    ) -> list[Document]:
        start_time = time.time()

        try:
            ascending = SortDirection.ASCENDING if asc else SortDirection.DESCENDING

            filtered_documents = (
                await self.collection.find(kwargs)
                .sort([(order_by, ascending)])
                .skip(skip)
                .limit(limit)
                .to_list()
            )

            duration_ms = (time.time() - start_time) * 1000

            logger.debug(
                "Filtered documents",
                collection=self.collection_name,
                filter_criteria=kwargs,
                order_by=order_by,
                ascending=asc,
                skip=skip,
                limit=limit,
                result_count=len(filtered_documents),
                duration_ms=duration_ms,
            )

            return filtered_documents

        except Exception as exc:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                "Failed to filter documents",
                collection=self.collection_name,
                filter_criteria=kwargs,
                error=str(exc),
                duration_ms=duration_ms,
                exc_info=True,
            )
            raise

    async def update_document(
        self,
        id: UUID,
        updated_document: Document,
    ) -> Optional[Document]:
        doc_to_update = await self.collection.get(id)

        if not doc_to_update:
            ExceptionHandler(self.collection).resource_not_found(id)

        for field in updated_document.model_fields.values():
            field_name = field.alias
            if hasattr(doc_to_update, field_name) and field_name not in ["id", "_id"]:
                setattr(
                    doc_to_update, field_name, getattr(updated_document, field_name)
                )
        return await doc_to_update.save() if doc_to_update else None
