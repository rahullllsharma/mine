from worker_safety_service.graphql.main import schema


def test_project_query_requires_project_id() -> None:
    query = """
    query TestProjectQueryRequiresProjectId{
      project {
        id
        name
      }
    }
    """

    result = schema.execute_sync(query)

    assert result.errors is not None
