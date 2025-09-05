from typing import Any

from tests.integration.conftest import ExecuteGQL

forms_list_query = """
    query TestQuery (
      $limit: Int,
      $offset: Int,
      $search: String,
      $formName: [String!],
      $formId: [String!],
      $formStatus: [FormStatus!],
      $projectIds: [UUID!],
      $createdByIds: [UUID!],
      $updatedByIds: [UUID!],
      $locationIds: [UUID!],
      $orderBy: [FormListOrderBy!],
      $startCreatedAt: Date,
      $endCreatedAt: Date,
      $startUpdatedAt: Date,
      $endUpdatedAt: Date,
      $startCompletedAt: Date,
      $endCompletedAt: Date,
      $startReportDate: Date,
      $endReportDate: Date,
      $adHoc: Boolean,
    ) {
      formsList(
        limit: $limit,
        offset: $offset,
        search: $search,
        orderBy: $orderBy,
        formName: $formName,
        formId: $formId,
        formStatus: $formStatus,
        projectIds: $projectIds,
        locationIds: $locationIds,
        createdByIds: $createdByIds,
        updatedByIds: $updatedByIds,
        startCreatedAt: $startCreatedAt,
        endCreatedAt: $endCreatedAt,
        startUpdatedAt: $startUpdatedAt,
        endUpdatedAt: $endUpdatedAt,
        startReportDate: $startReportDate,
        endReportDate: $endReportDate
        startCompletedAt: $startCompletedAt,
        endCompletedAt: $endCompletedAt,
        adHoc: $adHoc,
      ) {
        __typename
        completedAt
        completedBy {
          name
        }
        createdAt
        createdBy {
          name
        }
        id
        location {
          name
        }
        locationName
        status
        workPackage {
          name
        }
        formId
        supervisor {
          id
          name
          email
        }
      }
    }
"""


forms_list_query_with_manager_ids = """
    query TestQuery (
      $limit: Int,
      $offset: Int,
      $search: String,
      $formName: [String!],
      $formId: [String!],
      $formStatus: [FormStatus!],
      $projectIds: [UUID!],
      $createdByIds: [UUID!],
      $updatedByIds: [UUID!],
      $locationIds: [UUID!],
      $orderBy: [FormListOrderBy!],
      $startCreatedAt: Date,
      $endCreatedAt: Date,
      $startUpdatedAt: Date,
      $endUpdatedAt: Date,
      $startCompletedAt: Date,
      $endCompletedAt: Date,
      $startReportDate: Date,
      $endReportDate: Date,
      $adHoc: Boolean,
      $managerIds: [String!]
    ) {
      formsList(
        limit: $limit,
        offset: $offset,
        search: $search,
        orderBy: $orderBy,
        formName: $formName,
        formId: $formId,
        formStatus: $formStatus,
        projectIds: $projectIds,
        locationIds: $locationIds,
        createdByIds: $createdByIds,
        updatedByIds: $updatedByIds,
        startCreatedAt: $startCreatedAt,
        endCreatedAt: $endCreatedAt,
        startUpdatedAt: $startUpdatedAt,
        endUpdatedAt: $endUpdatedAt,
        startReportDate: $startReportDate,
        endReportDate: $endReportDate
        startCompletedAt: $startCompletedAt,
        endCompletedAt: $endCompletedAt,
        adHoc: $adHoc,
        managerIds: $managerIds,
      ) {
        __typename
        completedAt
        completedBy {
          name
        }
        createdAt
        createdBy {
          name
        }
        id
        location {
          name
        }
        locationName
        status
        workPackage {
          name
        }
        formId
      }
    }
"""

forms_list_count_query_with_manager_ids = """
    query TestQuery (
      $formName: [String!],
      $managerIds: [String!]
    ) {
      formsListCount(formName: $formName, managerIds: $managerIds)
    }
"""


async def call_forms_list_query(execute_gql: ExecuteGQL, **kwargs: Any) -> list[dict]:
    user = kwargs.pop("user", None)

    data = await execute_gql(query=forms_list_query, variables=kwargs, user=user)
    forms: list[dict] = data["formsList"]
    return forms


async def call_forms_list_query_with_manager_ids(
    execute_gql: ExecuteGQL, **kwargs: Any
) -> list[dict]:
    user = kwargs.pop("user", None)
    data = await execute_gql(
        query=forms_list_query_with_manager_ids, variables=kwargs, user=user
    )
    forms: list[dict] = data["formsList"]
    return forms


async def call_forms_list_count_query_with_manager_ids(
    execute_gql: ExecuteGQL, **kwargs: Any
) -> int:
    user = kwargs.pop("user", None)
    data = await execute_gql(
        query=forms_list_count_query_with_manager_ids, variables=kwargs, user=user
    )
    formsListCount: int = data["formsListCount"]
    return formsListCount
