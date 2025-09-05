import re
from copy import deepcopy
from datetime import datetime, time, timedelta, timezone
from typing import Any, Dict, Optional, Union
from uuid import UUID

from bson import Binary

from ws_customizable_workflow.models.base import (
    BaseFilterArgs,
    InclusiveType,
    OrderByFields,
)
from ws_customizable_workflow.models.form_models import Form, FormListRow, FormStatus
from ws_customizable_workflow.models.template_models import TemplateListRow


class AggregationPipelines:
    @staticmethod
    def process_filter_args(
        filter_args: BaseFilterArgs, search_fields: Optional[list[str]] = None
    ) -> Dict[str, Dict[str, Any]]:
        processed_filter_args: Dict[str, Any] = {}

        def process_range_based_filter_args(
            processed_arg_name: str,
            start_arg: Optional[datetime] = None,
            end_arg: Optional[datetime] = None,
            inclusive_type: InclusiveType = InclusiveType.START,
        ) -> None:
            """
            Processes range-based filter arguments with inclusive or exclusive bounds.

            Args:
                processed_arg_name (str): The name of the argument to process.
                start_arg (Optional[datetime]): The start datetime argument.
                end_arg (Optional[datetime]): The end datetime argument.
                inclusive_type (InclusiveType): Determines inclusivity (START, END, or BOTH).
            """
            nonlocal processed_filter_args

            # Map InclusiveType to MongoDB operators
            operator_map = {
                InclusiveType.START: ("$gte", "$lt"),
                InclusiveType.END: ("$gt", "$lte"),
                InclusiveType.BOTH: ("$gte", "$lte"),
            }

            start_op, end_op = operator_map[inclusive_type]

            if start_arg or end_arg:
                processed_filter_args[processed_arg_name] = {}
                if start_arg:
                    processed_filter_args[processed_arg_name][start_op] = start_arg
                if end_arg:
                    processed_filter_args[processed_arg_name][end_op] = end_arg

        # search if title contains by the given string
        if filter_args.titles:
            regex_pattern = "|".join(
                f"^{re.escape(title)}$" for title in filter_args.titles
            )
            processed_filter_args["properties.title"] = {
                "$regex": regex_pattern,
                "$options": "i",
            }
        if filter_args.title:
            processed_filter_args["properties.title"] = {"$eq": filter_args.title}

        if filter_args.template_unique_id:
            processed_filter_args["properties.template_unique_id"] = {
                "$eq": Binary.from_uuid(filter_args.template_unique_id)
            }

        # other filters
        if filter_args.status:
            processed_filter_args["properties.status"] = {"$in": filter_args.status}

        process_range_based_filter_args(
            "published_at",
            filter_args.published_at_start_date,
            filter_args.published_at_end_date,
        )
        process_range_based_filter_args(
            "updated_at",
            filter_args.updated_at_start_date,
            filter_args.updated_at_end_date,
        )
        process_range_based_filter_args(
            "created_at",
            filter_args.created_at_start_date,
            filter_args.created_at_end_date,
        )
        process_range_based_filter_args(
            "completed_at",
            filter_args.completed_at_start_date,
            filter_args.completed_at_end_date,
            InclusiveType.BOTH,
        )

        process_range_based_filter_args(
            "properties.report_start_date",
            filter_args.reported_at_start_date,
            filter_args.reported_at_end_date,
            InclusiveType.BOTH,
        )

        processed_filter_args["is_archived"] = {"$eq": filter_args.is_archived}

        if filter_args.is_latest_version is not None:
            processed_filter_args["is_latest_version"] = {
                "$eq": filter_args.is_latest_version
            }

        if filter_args.report_start_date is not None:
            # Get the datetime's date component
            report_date = filter_args.report_start_date.date()

            # Create start and end datetimes for the date in UTC time
            # Start of day: 00:00:00 UTC
            start_of_day = datetime.combine(report_date, time.min, tzinfo=timezone.utc)

            # Start of next day: 00:00:00 UTC (tomorrow)
            next_day = report_date + timedelta(days=1)
            start_of_next_day = datetime.combine(
                next_day, time.min, tzinfo=timezone.utc
            )

            # MongoDB date filtering: >= start of day AND < start of next day
            processed_filter_args["properties.report_start_date"] = {
                "$gte": start_of_day,
                "$lt": start_of_next_day,
            }

        if filter_args.search:
            search_pattern = re.escape(filter_args.search)
            search_regex = {
                "$regex": search_pattern,
                "$options": "i",
            }

            # Build the $or condition
            if search_fields:
                processed_filter_args["$or"] = [
                    {field: search_regex} for field in search_fields
                ]

        if filter_args.published_by:
            processed_filter_args["published_by.user_name"] = {
                "$in": filter_args.published_by
            }

        if filter_args.created_by:
            processed_filter_args["created_by.user_name"] = {
                "$in": filter_args.created_by
            }

        if filter_args.updated_by:
            processed_filter_args["updated_by.user_name"] = {
                "$in": filter_args.updated_by
            }
        if filter_args.work_package_id:
            processed_filter_args["metadata.work_package.id"] = {
                "$in": filter_args.work_package_id
            }

        if filter_args.location_id:
            processed_filter_args["metadata.location.id"] = {
                "$in": filter_args.location_id
            }
        if filter_args.region_id:
            processed_filter_args["metadata.region.id"] = {"$in": filter_args.region_id}

        if filter_args.supervisor_id:
            processed_filter_args["metadata.supervisor.id"] = {
                "$in": filter_args.supervisor_id
            }

        return processed_filter_args

    @staticmethod
    def process_fields_to_project(
        query: list[dict[str, dict]],
        display_model: Optional[
            Union[type[TemplateListRow], type[FormListRow], type[Form]]
        ] = None,
    ) -> list[dict[str, dict]]:
        # This function adds a project clause to query pipeline so that only
        # the fields which need to be projected are fetched rather than
        # fetching entire body of document

        if display_model:
            project_fields = {}
            for attr in display_model.model_fields.keys():
                if display_model == FormListRow and attr == "location_data":
                    project_fields[attr] = "$component_data.location_data"
                else:
                    project_fields[attr] = (
                        "$properties." + attr
                        if attr
                        in [
                            "title",
                            "status",
                            "template_unique_id",
                            "report_start_date",
                        ]
                        else "$" + attr
                    )
            query.append({"$project": project_fields})
        return query

    @staticmethod
    def get_nested_group_by_field(
        group_by_field: str,
        display_model: Optional[
            type[TemplateListRow] | type[FormListRow] | type[Form]
        ] = None,
    ) -> str:
        """
        Handles nested fields in the group_by operation based on the display model being used.

        Args:
            group_by_field: The original group_by field
            display_model: The model class being used for the query

        Returns:
            The properly nested field path for MongoDB aggregation
        """
        # Check if we need to adjust the field path for Form vs FormListRow
        # When using the full Form model, some fields like title are nested under properties
        if display_model == Form and group_by_field in [
            "title",
            "status",
            "report_start_date",
        ]:
            return f"properties.{group_by_field}"
        return group_by_field

    @classmethod
    def list_documents_query(
        cls,
        filter_args: BaseFilterArgs,
        display_model: Optional[
            Union[type[TemplateListRow], type[FormListRow], type[Form]]
        ] = None,
        search_fields: Optional[list[str]] = None,
    ) -> list[dict[str, dict]]:
        processed_filter_args = cls.process_filter_args(filter_args, search_fields)

        query = [{"$match": processed_filter_args}]

        query = cls.process_fields_to_project(display_model=display_model, query=query)
        if filter_args.group_by:
            # Get the properly nested group_by field path based on the display model
            group_by_field = cls.get_nested_group_by_field(
                filter_args.group_by, display_model
            )

            query.append(
                {
                    "$group": {
                        "_id": f"${group_by_field}",  # type: ignore
                        "group_by_key": {"$first": f"${group_by_field}"},
                        "forms": {"$push": "$$ROOT"},
                    }
                }
            )
        return query

    @classmethod
    def get_count_of_documents_query(cls, query: list[dict]) -> list[dict[str, Any]]:
        query = deepcopy(query)
        query.append({"$count": "document_count"})
        return query

    @classmethod
    def apply_order_skip_limit_to_query(
        cls,
        query: list[dict],
        order_by: str,
        desc: bool,
        skip: int,
        limit: int,
    ) -> None:
        sort_clause = {"$sort": {order_by: -1 if desc else 1}}
        if order_by in [OrderByFields.TITLE]:
            if len(query) > 0 and query[0].get("$project"):
                query[0]["$project"]["lower_case_title"] = {
                    "$toLower": "$properties.title"
                }
                sort_clause["$sort"] = {"lower_case_title": -1 if desc else 1}
        query.append(sort_clause)
        query.append({"$skip": skip})
        query.append({"$limit": limit})

    @classmethod
    def template_title_check(cls, title: str) -> list[dict]:
        return [
            {
                "$match": {
                    "properties.title": {
                        "$regex": f"^{re.escape(title)}$",
                        "$options": "i",
                    }
                }
            }
        ]

    @staticmethod
    async def fetch_user_forms_with_prepopulation_pipeline(
        template_names: list[str], user_id: UUID
    ) -> list[dict[str, Any]]:
        return await Form.aggregate(
            [
                {
                    "$match": {
                        "properties.title": {"$in": template_names},
                        "properties.status": FormStatus.COMPLETE.value,
                        "is_archived": False,
                        "updated_by.id": Binary.from_uuid(user_id),
                    }
                },
                {"$sort": {"updated_at": -1}},
                {
                    "$group": {
                        "_id": "$properties.title",
                        "first_doc": {"$first": "$$ROOT"},
                    }
                },
            ]
        ).to_list()
