from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple, Union, cast
from uuid import UUID

from fastapi import HTTPException, status

from ws_customizable_workflow.exceptions import PrePopulationError
from ws_customizable_workflow.managers.services.pre_selection_rules import PreSelection
from ws_customizable_workflow.models.base import FormStatus, PrePopulationRules
from ws_customizable_workflow.models.element_models import ElementType
from ws_customizable_workflow.models.form_models import Form
from ws_customizable_workflow.models.template_models import Template
from ws_customizable_workflow.models.users import UserBase


class PathParser:
    """Handles path parsing and element retrieval from data structures."""

    def _graceful_fail(
        self,
        error_message: str,
        status_code: int = status.HTTP_404_NOT_FOUND,
        graceful_fail: bool = False,
    ) -> Optional[Any]:
        """
        Hidden method for graceful error handling.

        This method provides a consistent way to handle errors gracefully
        throughout the class. It either returns None (for graceful_fail=True)
        or raises a PrePopulationError (for graceful_fail=False).

        Args:
            error_message: The error message to display
            status_code: HTTP status code for the error
            graceful_fail: If True, returns None instead of raising exception

        Returns:
            None if graceful_fail=True

        Raises:
            PrePopulationError: If graceful_fail=False
        """
        if graceful_fail:
            return None
        raise PrePopulationError(error_message, status_code=status_code)

    def get_element_from_uuid_path(
        self,
        data_source: Optional[Union[Dict[str, Any], List[Any]]],
        uuid_path: str,
        graceful_fail: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """
        Find an element in the data structure using a UUID path.

        This function combines the functionality of finding a path and extracting
        the value at that path. It traverses the data structure looking for elements
        whose "id" field matches the UUIDs in the path.

        Args:
            data_source: The data structure to search in (dict or list)
            uuid_path: A path string with UUIDs separated by "/" (e.g., "uuid1/uuid2/uuid3")
            graceful_fail: If True, returns None when element not found instead of raising an exception

        Returns:
            The found element dictionary or None if not found (when graceful_fail=True)

        Raises:
            PrePopulationError: When element not found and graceful_fail=False, or on validation errors
        """
        if not uuid_path:
            return self._graceful_fail(
                "Empty UUID path provided",
                status_code=status.HTTP_400_BAD_REQUEST,
                graceful_fail=graceful_fail,
            )

        # Handle paths with only slashes
        if uuid_path.strip("/") == "":
            return self._graceful_fail(
                "Empty UUID path provided",
                status_code=status.HTTP_400_BAD_REQUEST,
                graceful_fail=graceful_fail,
            )

        if data_source is None:
            return self._graceful_fail(
                "Data source is None",
                status_code=status.HTTP_400_BAD_REQUEST,
                graceful_fail=graceful_fail,
            )

        # Split the UUID path into individual UUIDs
        target_uuids = uuid_path.split("/")

        # Use iterative approach with stack
        # Stack contains tuples of (data, remaining_uuids, found_path)
        stack: List[Tuple[Union[Dict[str, Any], List[Any]], List[str], List[str]]] = [
            (data_source, target_uuids, [])
        ]

        while stack:
            current_data, remaining_uuids, found_path = stack.pop()

            if not remaining_uuids:
                continue

            current_uuid = remaining_uuids[0]
            next_uuids = remaining_uuids[1:]

            if isinstance(current_data, dict):
                # Check if current dict has the matching ID
                if current_data.get("id") == current_uuid:
                    # If this is the last UUID in the path, validate and return the element
                    if not next_uuids:
                        # Validate the element structure inline
                        if not isinstance(current_data, dict):
                            return self._graceful_fail(
                                "Found element is not a dictionary",
                                status_code=status.HTTP_400_BAD_REQUEST,
                                graceful_fail=graceful_fail,
                            )

                        if "properties" not in current_data:
                            return self._graceful_fail(
                                f"'properties' key not found in element with id: {current_uuid}",
                                status_code=status.HTTP_400_BAD_REQUEST,
                                graceful_fail=graceful_fail,
                            )

                        if "type" not in current_data:
                            return self._graceful_fail(
                                f"'type' key not found in element with id: {current_uuid}",
                                status_code=status.HTTP_400_BAD_REQUEST,
                                graceful_fail=graceful_fail,
                            )

                        return current_data

                    # Found a matching segment - clear stack and continue only from this path
                    stack.clear()

                    # Continue searching in contents
                    if "contents" in current_data and isinstance(
                        current_data["contents"], (dict, list)
                    ):
                        stack.append(
                            (
                                current_data["contents"],
                                next_uuids,
                                found_path + [current_uuid],
                            )
                        )

                    # If no properties/contents to search, continue with remaining siblings
                    if not stack:
                        # Search in parent's other children
                        continue

                else:
                    # No match found - search recursively in all dict values
                    for value in current_data.values():
                        if (
                            isinstance(value, (dict, list))
                            and "contents" in current_data
                        ):
                            stack.append((value, remaining_uuids, found_path))

            elif isinstance(current_data, list):
                # Search recursively in all list items
                for item in current_data:
                    if isinstance(item, (dict, list)):
                        stack.append((item, remaining_uuids, found_path))
                    elif isinstance(item, str) and item == current_uuid:
                        # Found a string that matches the UUID but it's not a dict
                        if not next_uuids:
                            return self._graceful_fail(
                                "Found element is not a dictionary",
                                status_code=status.HTTP_400_BAD_REQUEST,
                                graceful_fail=graceful_fail,
                            )

        # Element not found - provide detailed error information
        return self._graceful_fail(
            f"Element not found for UUID path: {uuid_path}. "
            f"Path segments: {target_uuids}",
            status_code=status.HTTP_404_NOT_FOUND,
            graceful_fail=graceful_fail,
        )


class UserValueHandler:
    """Handles getting and setting user values in elements."""

    def get_user_value(self, element_dict: Dict[str, Any]) -> Optional[Any]:
        """
        Get user value from element properties.

        Args:
            element_dict: The element dictionary

        Returns:
            The user value or None if not found
        """
        if element_dict is None:
            return None
        properties = element_dict.get("properties")
        if properties is None:
            return None
        return properties.get("user_value")

    def get_user_other_value(self, element_dict: Dict[str, Any]) -> Optional[Any]:
        """
        Get user other value from element properties.

        Args:
            element_dict: The element dictionary

        Returns:
            The user other value or None if not found
        """
        if element_dict is None:
            return None
        properties = element_dict.get("properties")
        if properties is None:
            return None
        return properties.get("user_other_value")

    def set_user_value(
        self,
        element_dict: Dict[str, Any],
        user_value: Any,
        user_other_value: Any = None,
    ) -> None:
        """
        Set user value in element properties.
        For dropdown elements, both user_value and user_other_value are set.

        Args:
            element_dict: The element dictionary to update
            user_value: The user value to set
            user_other_value: The user other value to set (optional)
        """
        if "properties" not in element_dict:
            element_dict["properties"] = {}

        element_dict["properties"]["user_value"] = user_value

        # For dropdown elements, always set user_other_value if provided
        if user_other_value is not None:
            element_dict["properties"]["user_other_value"] = user_other_value


class RuleRegistry:
    """Manages rule handlers and their registration."""

    def __init__(self) -> None:
        self.rule_handlers: Dict[str, Callable[..., Awaitable[Any]]] = {}

    def register_rule(
        self, rule_name: str, rule_handler: Callable[..., Awaitable[Any]]
    ) -> None:
        """Register a rule handler."""
        self.rule_handlers[rule_name] = rule_handler

    def get_rule(self, rule_name: str) -> Callable[..., Awaitable[Any]]:
        """Get a rule handler by name."""
        if rule_name not in self.rule_handlers:
            raise ValueError(f"Rule '{rule_name}' not found")
        return self.rule_handlers[rule_name]

    def get_all_rules(self) -> Dict[str, Callable[..., Awaitable[Any]]]:
        """Get all registered rules."""
        return self.rule_handlers.copy()

    def initialize_rules(
        self,
        user_details: UserBase,
        prefetched_forms: Dict[str, Form],
        use_prefetched_only: bool,
    ) -> None:
        """
        Initialize and register all available rules with the given context.

        Args:
            user_details: User details for rule context
            prefetched_forms: Prefetched forms for rule context
            use_prefetched_only: Flag to use prefetched forms only
        """
        # Register user last completed form rule
        user_handler_last_completed_rule = RuleUserLastCompletedForm(
            user_details=user_details,
            prefetched_forms=prefetched_forms,
            use_prefetched_only=use_prefetched_only,
        )
        self.register_rule(
            PrePopulationRules.USER_LAST_COMPLETED.value,
            user_handler_last_completed_rule,
        )


class RuleUserLastCompletedForm:
    """Rule handler for user's last completed form."""

    def __init__(
        self,
        user_details: UserBase,
        prefetched_forms: Dict[str, Form],
        use_prefetched_only: bool,
    ):
        self.user_details = user_details
        self.prefetched_forms = prefetched_forms
        self.use_prefetched_only = use_prefetched_only
        self.user_value_handler = UserValueHandler()

    async def __call__(
        self,
        *,
        pre_populate_element_type: ElementType,
        uuid_path: str,
        template_title: str,
    ) -> dict:
        """
        Fetch user last completed form, find the dict located at the given dict_path,
        check the type of the dict at the given dict_path, get and return user_value.
        """

        rule_result_dict = {"user_value": None, "user_other_value": None}

        user_id = self.user_details.id

        user_last_completed_form = None
        if self.prefetched_forms:
            user_last_completed_form = await self._get_form_from_prefetched(
                template_title
            )

        if not user_last_completed_form and not self.use_prefetched_only:
            user_last_completed_form = await self._get_form_from_database(
                template_title, user_id
            )

        if not user_last_completed_form:
            return rule_result_dict

        # Handle both dictionary and Form object cases
        user_last_completed_form_dict = (
            user_last_completed_form.model_dump()
            if hasattr(user_last_completed_form, "model_dump")
            else user_last_completed_form
        )

        # Asserting that after model_dump, the 'contents'
        # key will hold a dict, list, or None.
        contents_data_source = cast(
            Optional[Union[Dict[str, Any], List[Any]]],
            user_last_completed_form_dict.get("contents"),
        )

        # Fetch the dictionary located at the given dict_path
        target_dict = PathParser().get_element_from_uuid_path(
            data_source=contents_data_source,
            uuid_path=uuid_path,
            graceful_fail=True,
        )

        if target_dict is None:
            return rule_result_dict

        ppl_path = target_dict.get("id", "")
        is_ppl_path = uuid_path.split("/")[-1] == ppl_path
        if not is_ppl_path:
            return rule_result_dict

        # Check the type of the found dictionary
        element_type = target_dict.get("type")
        expected_type = (
            pre_populate_element_type.value
            if hasattr(pre_populate_element_type, "value")
            else pre_populate_element_type
        )
        if element_type != expected_type:
            raise PrePopulationError(
                "Element Type mismatch",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        # Fetch and return the user_value from properties
        rule_result_dict["user_value"] = self.user_value_handler.get_user_value(
            target_dict
        )

        req_user_value = self.user_value_handler.get_user_value(target_dict)
        # For dropdown elements, also get user_other_value
        dropdown_type = (
            ElementType.DROPDOWN.value
            if hasattr(ElementType.DROPDOWN, "value")
            else ElementType.DROPDOWN
        )
        if (
            expected_type == dropdown_type
            and target_dict.get("properties", {}).get("include_other_option")
            and req_user_value
            and isinstance(req_user_value, (list, tuple))
            and "other" in req_user_value
        ):
            rule_result_dict[
                "user_other_value"
            ] = self.user_value_handler.get_user_other_value(target_dict)
        else:
            rule_result_dict["user_other_value"] = None

        return rule_result_dict

    async def _get_form_from_prefetched(
        self, template_title: str
    ) -> Optional[Union[Form, dict]]:
        """
        Get the last completed form from prefetched forms if available.
        Returns None if no form is found in prefetched forms.
        """
        if (
            not self.prefetched_forms
            or str(template_title) not in self.prefetched_forms
        ):
            return None
        return self.prefetched_forms.get(str(template_title))

    async def _get_form_from_database(
        self, template_title: str, user_id: UUID
    ) -> Optional[Form]:
        """
        Fetch the last completed form from the database.
        Returns None if no form is found in the database.
        """
        return await Form.find_one(
            {
                "properties.title": template_title,
                "properties.status": FormStatus.COMPLETE.value,
                "updated_by.id": user_id,
                "is_archived": False,
            },
            sort=[("updated_at", -1)],
        )


class PrePopulation:
    """
    Handles pre-population rules for templates.
    Single Responsibility: Orchestrating the prepopulation process.
    """

    def __init__(
        self,
        template: Template,
        user_details: UserBase,
        prefetched_forms: Optional[Dict[str, Form]] = None,
        use_prefetched_only: bool = False,
    ) -> None:
        self.template = template.model_dump()
        self.rule_paths: Dict[str, List[str]] = (
            self.template.get("pre_population_rule_paths", {}) or {}
        )
        self.user_details: UserBase = user_details
        self.prefetched_forms: Dict[str, Form] = prefetched_forms or {}
        self.use_prefetched_only = use_prefetched_only

        # Initialize helper components
        self.path_parser = PathParser()
        self.user_value_handler = UserValueHandler()
        self.rule_registry = RuleRegistry()

        # Initialize and register all rules
        self.rule_registry.initialize_rules(
            user_details=self.user_details,
            prefetched_forms=self.prefetched_forms,
            use_prefetched_only=self.use_prefetched_only,
        )

    async def process_rules(self) -> None:
        """
        Process all rules and update the JSON structure accordingly.
        """
        for rule_name, uuid_path_list in self.rule_paths.items():
            for uuid_path in uuid_path_list:
                try:
                    req_element_dict = self.path_parser.get_element_from_uuid_path(
                        data_source=self.template.get("contents"),
                        uuid_path=uuid_path,
                        graceful_fail=False,
                    )

                    if req_element_dict is None:
                        continue

                    pre_populate_element_type = req_element_dict.get("type")

                    if rule_name in self.rule_registry.rule_handlers:
                        req_user_value_dict = await self.rule_registry.rule_handlers[
                            rule_name
                        ](
                            **{
                                "pre_populate_element_type": pre_populate_element_type,
                                "uuid_path": uuid_path,
                                "template_title": self.template.get(
                                    "properties", {}
                                ).get("title"),
                            }
                        )

                        # Handle dropdown elements specially
                        if pre_populate_element_type == ElementType.DROPDOWN.value:
                            # For dropdowns, always set both user_value and user_other_value
                            self.user_value_handler.set_user_value(
                                req_element_dict,
                                req_user_value_dict.get("user_value"),
                                req_user_value_dict.get("user_other_value"),
                            )
                        else:
                            # For non-dropdown elements, only set user_value
                            self.user_value_handler.set_user_value(
                                req_element_dict,
                                req_user_value_dict.get("user_value"),
                            )
                except PrePopulationError as e:
                    raise HTTPException(status_code=e.status_code, detail=str(e))
                except Exception as e:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Unexpected error processing rule '{rule_name}' for uuid_path '{uuid_path}': {e}",
                    )

    @staticmethod
    async def prepopulate_templates(
        templates: list[Template],
        user_details: UserBase,
        prefetched_forms: dict[str, Form],
        use_prefetched_only: bool = False,
        preselect_work_types: bool = False,
    ) -> list[Template]:
        prepopulated_templates = []
        for template in templates:
            pre_population = PrePopulation(
                template=template,
                user_details=user_details,
                prefetched_forms=prefetched_forms,
                use_prefetched_only=use_prefetched_only,
            )
            await pre_population.process_rules()
            prepopulated_template = Template.model_validate(pre_population.template)
            if preselect_work_types and prepopulated_template.settings.work_types:
                prepopulated_template.settings.work_types = (
                    await PreSelection.preselect_work_types_for_template(
                        prepopulated_template.properties.title,
                        prepopulated_template.settings.work_types,
                        prefetched_forms,
                    )
                )
            prepopulated_templates.append(prepopulated_template)

        return prepopulated_templates
