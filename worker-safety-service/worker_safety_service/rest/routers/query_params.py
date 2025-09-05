from fastapi import Query

after = Query(
    default=None,
    alias="page[after]",
    description="Skip the returned cursor to this element",
)
limit = Query(
    default=20,
    le=200,
    ge=1,
    alias="page[limit]",
    description="Maximum number of elements returned",
)
location_ids = Query(
    default=None,
    alias="filter[location]",
    description="Filter results to those related to this activity id",
)
external_keys = Query(
    default=None,
    alias="filter[externalKey]",
    description="filter by external key",
)
activity_ids = Query(
    default=None,
    alias="filter[activity]",
    description="Filter results to those related to this activity id",
)
work_package_ids = Query(
    default=None,
    alias="filter[work-package]",
    description="Filter resources associated with this work package",
)
activity_external_keys = Query(
    default=None,
    alias="filter[activity][externalKey]",
    description="filter results to those related to this activity id",
)
show_summary = Query(
    default=False,
    alias="page[showSummary]",
    description="Return the number of total and remaining elements. Because these properties are expensive to compute, they can be omitted by the server to preserve system integrity.",
)
feature_names = Query(
    default=None,
    alias="filter[featureName]",
    description="filter by feature name",
)
include_archived = Query(
    default=False,
    alias="filter[include_archived]",
    description="Includes archived records as well in the result",
)
