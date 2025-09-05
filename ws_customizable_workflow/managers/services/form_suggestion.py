from typing import Any, Dict, List, Set, Tuple
from uuid import UUID

from ws_customizable_workflow.managers.DBCRUD.dbcrud import CRUD
from ws_customizable_workflow.models.base import (  # CrewInformation,
    FormStatus,
    SuggestionType,
)
from ws_customizable_workflow.models.element_models import ElementType
from ws_customizable_workflow.models.form_models import Form
from ws_customizable_workflow.models.users import UserBase
from ws_customizable_workflow.urbint_logging import get_logger

logger = get_logger(__name__)

forms_crud_manager = CRUD(Form)


class FormElementSuggestionExtractor:
    """
    Provides extraction and cleaning of user values for a specified element type from recent forms.
    Supports both dictionary and Pydantic model traversal, and applies suggestion-type-specific cleaning logic.
    Used to generate suggestions for form elements based on a user's recent form submissions.
    """

    def __init__(
        self,
        template_id: UUID,
        element_type: ElementType,
        user_details: UserBase,
        suggestion_type: SuggestionType,
    ):
        """
        Initializes the extractor with template, element type, user, and suggestion type.
        """
        self.template_id = template_id
        self.element_type = element_type
        self.user_details = user_details
        self.suggestion_type = suggestion_type

    @staticmethod
    def get_all_element_type_paths(template: dict, element_type: str) -> List[List]:
        """
        Iteratively find all paths to elements of the given type inside any nested 'contents' arrays and
        returns the List of paths (each path is a list of keys/indices) to elements of the given type.
        Here we are using DFS approach.
        """
        paths = []
        stack = []

        # Start with all top-level contents
        contents = template.get("contents")
        if isinstance(contents, list):
            for idx, item in enumerate(contents):
                stack.append((item, ["contents", idx]))

        while stack:
            current, path = stack.pop()
            if isinstance(current, dict):
                if current.get("type") == element_type:
                    paths.append(path)
                # Go deeper if 'contents' exists and is a list
                sub_contents = current.get("contents")
                if isinstance(sub_contents, list):
                    for idx, item in enumerate(sub_contents):
                        stack.append((item, path + ["contents", idx]))
        return paths

    async def extract_suggestions(self) -> List[Any]:
        """
        Main entrypoint for extracting suggestions based on the configured suggestion type.
        """
        if (
            self.element_type == ElementType.PERSONNEL_COMPONENT
            and self.suggestion_type == SuggestionType.RECENTLY_SELECTED_CREW_DETAILS
        ):
            return (
                await self.suggestion_for_recently_selected_crew_details_for_personnel_component()
            )
        return []

    async def suggestion_for_recently_selected_crew_details_for_personnel_component(
        self,
    ) -> List[Dict[Any, Any]]:
        """
        Returns a list of filtered crew details for a personnel component
        from the most recent completed forms for the given template and user.

        The method:
        - Fetches up to 5 most recently updated, completed, and non-archived forms for the user and template.
        - Finds all paths to elements of the specified type within the first form's structure.
        - For each matching element in each form, retrieves the 'user_value' from its properties.
        - Cleans each user value by removing 'selected_attribute_ids' from any dict and
          removing 'signature' from any 'crew_details' dict, using an iterative approach.
        - Aggregates and returns all cleaned user values as a flat list.
        """
        forms = await forms_crud_manager.filter_documents_by_attributes(
            limit=5,
            asc=False,
            skip=0,
            order_by="updated_at",
            **{
                "is_archived": False,
                "template_id": self.template_id,
                "properties.status": FormStatus.COMPLETE,
                "updated_by.id": self.user_details.id,
            },
        )

        if not forms:
            return []

        first_form_dict = forms[0].model_dump()
        element_paths = self.get_all_element_type_paths(
            template=first_form_dict, element_type=self.element_type.value
        )

        user_values: List[dict] = []
        seen: Set[Tuple] = set()

        for form in forms:
            form_dict = form.model_dump()
            for path in element_paths:
                try:
                    current = form_dict
                    for key in path:
                        current = current[key]
                    # Get properties.user_value using dict access
                    user_value = current.get("properties", {}).get("user_value")
                    if user_value is not None and isinstance(user_value, list):
                        # cleaned is expected to be a list of dicts
                        for item in user_value:
                            (item.get("crew_details", {}) or {}).pop("signature", None)
                            item.pop("selected_attribute_ids", None)
                            crew = item.get("crew_details")
                            if crew:
                                # Build a tuple of the unique fields for deduplication
                                unique_key = tuple(
                                    crew.get(field)
                                    for field in (
                                        "name",
                                        "job_title",
                                        "employee_number",
                                        "display_name",
                                        "email",
                                    )
                                )
                                if unique_key not in seen:
                                    seen.add(unique_key)
                                    user_values.append(crew)
                except Exception as exc:
                    logger.error(
                        f"Failed to extract crew details for path {path}",
                        workflow="form_suggestion",
                        form_id=str(getattr(form, "id", None)),
                        error=str(exc),
                        exc_info=True,
                    )
                    continue  # Skip if path is invalid for this form

        return user_values
