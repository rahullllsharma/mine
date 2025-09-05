from typing import Any, List

from ws_customizable_workflow.models.template_models import TemplateWorkType
from ws_customizable_workflow.utils.helpers import decode_binary_uuid_id


class PreSelection:
    @staticmethod
    async def preselect_work_types_for_template(
        template_name: str,
        template_work_types: List[TemplateWorkType],
        user_completed_forms: dict[str, Any],
    ) -> List[TemplateWorkType]:
        user_completed_form = user_completed_forms.get(template_name)
        if not user_completed_form:
            # Return early if no user completed form found. Pre populate is False by default.
            return template_work_types

        user_completed_form_metadata = user_completed_form.get("metadata") or {}
        last_selected_work_types = user_completed_form_metadata.get("work_types")

        if not last_selected_work_types:
            return template_work_types

        # Create a set of last selected work type IDs
        last_selected_ids = {
            decode_binary_uuid_id(work_type["id"])
            for work_type in last_selected_work_types
        }

        # Update only the prepopulate flag for matching work types
        for work_type in template_work_types:
            if str(work_type.id) in last_selected_ids:
                work_type.prepopulate = True

        return template_work_types
