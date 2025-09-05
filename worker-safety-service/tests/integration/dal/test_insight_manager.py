import pytest
from pydantic.error_wrappers import ValidationError

from tests.factories import InsightFactory, TenantFactory
from worker_safety_service.dal.insight_manager import InsightManager
from worker_safety_service.exceptions import DuplicateKeyException
from worker_safety_service.models import (
    AsyncSession,
    CreateInsightInput,
    Tenant,
    UpdateInsightInput,
)
from worker_safety_service.urbint_logging import get_logger

logger = get_logger(__name__)


# Successfully creating an insight
@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_insight(db_session: AsyncSession) -> None:
    tenant = await TenantFactory.persist(db_session)
    insight_manager = InsightManager(db_session)
    insights = await insight_manager.get_all(tenant_id=tenant.id)
    assert len(insights) == 0

    new_insight = await insight_manager.create(
        CreateInsightInput(
            name="test1",
            url="https://dummy.insight.com/abc",
            description="test_description",
        ),
        tenant_id=tenant.id,
    )
    assert new_insight
    assert new_insight.name == "test1"
    assert new_insight.url == "https://dummy.insight.com/abc"
    assert new_insight.description == "test_description"
    assert new_insight.tenant == tenant
    assert new_insight.visibility
    assert new_insight.archived_at is None
    assert new_insight.ordinal == 1

    insights = await insight_manager.get_all(tenant_id=tenant.id)
    assert len(insights) == 1

    new_insight = await insight_manager.create(
        CreateInsightInput(
            name="test2",
            url="https://dummy.insight.com/abc1",
            description="test_description",
        ),
        tenant_id=tenant.id,
    )
    assert new_insight.name == "test2"
    assert new_insight.url == "https://dummy.insight.com/abc1"
    assert new_insight.description == "test_description"
    assert new_insight.tenant == tenant
    assert new_insight.visibility
    assert new_insight.archived_at is None
    assert new_insight.ordinal == 2

    insights = await insight_manager.get_all(tenant_id=tenant.id)
    assert len(insights) == 2


# Successfully updating an insight
@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_insight(db_session: AsyncSession) -> None:
    tenant = await TenantFactory.persist(db_session)
    db_insights = await InsightFactory.persist_many(
        db_session, tenant_id=tenant.id, size=3
    )
    insight_manager = InsightManager(db_session)
    insight_to_be_updated = db_insights[0]
    assert insight_to_be_updated.name
    old_url = insight_to_be_updated.url
    old_description = insight_to_be_updated.description
    assert insight_to_be_updated.visibility
    assert insight_to_be_updated.archived_at is None
    assert insight_to_be_updated.ordinal

    await insight_manager.update(
        id=insight_to_be_updated.id,
        input=UpdateInsightInput(name="updated_name_in_test"),
        tenant_id=tenant.id,
    )
    await db_session.refresh(insight_to_be_updated)
    assert insight_to_be_updated.name == "updated_name_in_test"
    assert insight_to_be_updated.url == old_url
    assert insight_to_be_updated.description == old_description
    assert insight_to_be_updated.tenant == tenant
    assert insight_to_be_updated.visibility
    assert insight_to_be_updated.archived_at is None
    assert insight_to_be_updated.ordinal == 2


# Successfully deleting an insight
@pytest.mark.asyncio
@pytest.mark.integration
async def test_archive_insight(db_session: AsyncSession) -> None:
    tenant = await TenantFactory.persist(db_session)
    db_insights = []
    for i in range(1, 4):
        insight = await InsightFactory.persist(
            db_session, tenant_id=tenant.id, ordinal=i
        )
        db_insights.append(insight)

    insight_manager = InsightManager(db_session)

    insight_to_be_archived = db_insights[1]
    assert insight_to_be_archived.archived_at is None

    assert await insight_manager.archive(
        id=insight_to_be_archived.id, tenant_id=tenant.id
    )

    await db_session.refresh(insight_to_be_archived)
    assert insight_to_be_archived.archived_at
    assert insight_to_be_archived.ordinal == -1

    await db_session.refresh(db_insights[0])
    assert not db_insights[0].archived_at
    assert db_insights[0].ordinal == 1


# Successfully reorder insights
@pytest.mark.asyncio
@pytest.mark.integration
async def test_reorder_insight(db_session: AsyncSession) -> None:
    tenant = await TenantFactory.persist(db_session)
    insight_manager = InsightManager(db_session)
    await reorder_insights_for_test(tenant=tenant, insight_manager=insight_manager)

    reordered_insights = await insight_manager.get_all(tenant.id)
    assert len(reordered_insights) == 10

    assert reordered_insights[0].name == "test5"
    assert reordered_insights[1].name == "test4"
    assert reordered_insights[2].name == "test3"
    assert reordered_insights[3].name == "test2"
    assert reordered_insights[4].name == "test1"
    assert reordered_insights[5].name == "test6"
    assert reordered_insights[6].name == "test7"
    assert reordered_insights[7].name == "test8"
    assert reordered_insights[8].name == "test9"
    assert reordered_insights[9].name == "test10"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_post_reordering_new_insight_should_have_the_highest_priority(
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    insight_manager = InsightManager(db_session)
    await reorder_insights_for_test(tenant=tenant, insight_manager=insight_manager)

    insight = await insight_manager.create(
        CreateInsightInput(
            name="new_insight_post_reordering",
            url="https://dummy.insight.com/abc1",
            description="test_description",
        ),
        tenant_id=tenant.id,
    )
    assert insight
    assert insight.ordinal == 11

    insights = await insight_manager.get_all(tenant.id)
    assert len(insights) == 11
    assert insights[0].name == "new_insight_post_reordering"
    assert insights[1].name == "test5"
    assert insights[2].name == "test4"
    assert insights[3].name == "test3"
    assert insights[4].name == "test2"
    assert insights[5].name == "test1"
    assert insights[6].name == "test6"
    assert insights[7].name == "test7"
    assert insights[8].name == "test8"
    assert insights[9].name == "test9"
    assert insights[10].name == "test10"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_post_archiving_first_insight_priority_should_change(
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    insight_manager = InsightManager(db_session)
    await reorder_insights_for_test(tenant=tenant, insight_manager=insight_manager)
    insights = await insight_manager.get_all(tenant.id)
    assert len(insights) == 10
    assert await insight_manager.archive(insights[0].id, tenant.id)
    await db_session.refresh(insights[0])
    assert insights[0].ordinal == -1
    assert insights[0].archived_at

    insights = await insight_manager.get_all(tenant.id)
    assert len(insights) == 9
    assert insights[0].name == "test4"
    assert insights[1].name == "test3"
    assert insights[2].name == "test2"
    assert insights[3].name == "test1"
    assert insights[4].name == "test6"
    assert insights[5].name == "test7"
    assert insights[6].name == "test8"
    assert insights[7].name == "test9"
    assert insights[8].name == "test10"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_post_archiving_middle_insight_priority_should_change(
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    insight_manager = InsightManager(db_session)
    await reorder_insights_for_test(tenant=tenant, insight_manager=insight_manager)
    insights = await insight_manager.get_all(tenant.id)
    assert len(insights) == 10
    assert await insight_manager.archive(insights[3].id, tenant.id)
    await db_session.refresh(insights[3])
    assert insights[3].ordinal == -1
    assert insights[3].archived_at

    insights = await insight_manager.get_all(tenant.id)
    assert len(insights) == 9
    assert insights[0].name == "test5"
    assert insights[1].name == "test4"
    assert insights[2].name == "test3"
    assert insights[3].name == "test1"
    assert insights[4].name == "test6"
    assert insights[5].name == "test7"
    assert insights[6].name == "test8"
    assert insights[7].name == "test9"
    assert insights[8].name == "test10"


# Successfully querying all insight for a tenant
@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_insights(db_session: AsyncSession) -> None:
    tenant = await TenantFactory.persist(db_session)
    insight_manager = InsightManager(db_session)
    await create_10_insights(tenant=tenant, insight_manager=insight_manager)
    insights_all = await insight_manager.get_all(tenant.id)
    assert len(insights_all) == 10
    insights_first_5 = await insight_manager.get_all(tenant.id, limit=5)
    assert len(insights_first_5) == 5
    insights_last_3 = await insight_manager.get_all(
        tenant.id, limit=3, after=insights_all[-4].id
    )
    assert len(insights_last_3) == 3


# Should not be able to create an insight if mandatory fields are not provided
@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_insight_error_missing_required_fields(
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    insight_manager = InsightManager(db_session)
    with pytest.raises(ValidationError):
        await insight_manager.create(
            CreateInsightInput(  # type:ignore # name missing
                url="https://dummy.insight.com/abc",
                description="test_description",
            ),
            tenant_id=tenant.id,
        )
    # logger.debug(f"ERROR --> {e.value.args[0]}")


# Should not be able to create duplicate insights(name cannot be duplicate)
@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_insight_error_duplicate_name(
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    insight_manager = InsightManager(db_session)
    await create_10_insights(tenant=tenant, insight_manager=insight_manager)
    with pytest.raises(DuplicateKeyException) as e:
        await insight_manager.create(
            CreateInsightInput(
                name="test1",
                url="https://dummy.insight.com/abc",
                description="test_description",
            ),
            tenant_id=tenant.id,
        )

    assert (
        e.value.args[0]
        == "Insight with same name already exists. Please give a unique name"
    )

    # case insensitive test for create
    with pytest.raises(DuplicateKeyException) as e:
        await insight_manager.create(
            CreateInsightInput(
                name="tESt1",
                url="https://dummy.insight.com/abc",
                description="test_description",
            ),
            tenant_id=tenant.id,
        )

    assert (
        e.value.args[0]
        == "Insight with same name already exists. Please give a unique name"
    )

    # case insensitive test for update
    existing_insights = await insight_manager.get_all(tenant_id=tenant.id, limit=2)
    with pytest.raises(DuplicateKeyException) as e:
        await insight_manager.update(
            id=existing_insights[0].id,
            input=UpdateInsightInput(
                name="tESt1",
                url="https://dummy.insight.com/abc",
                description="test_description",
            ),
            tenant_id=tenant.id,
        )

    assert (
        e.value.args[0]
        == "Insight with same name already exists. Please give a unique name"
    )


# Cannot create an insight with invalid url
@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_insight_error_invalid_url(db_session: AsyncSession) -> None:
    tenant = await TenantFactory.persist(db_session)
    insight_manager = InsightManager(db_session)
    with pytest.raises(ValidationError):
        await insight_manager.create(
            CreateInsightInput(
                name="test1",
                url="www://dummy.insight.com/abc",
                description="test_description",
            ),
            tenant_id=tenant.id,
        )
    # logger.debug(f"{e.value.args[0]}")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_insight_with_archived_insight_name(
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    db_insights = []
    for i in range(1, 4):
        insight = await InsightFactory.persist(
            db_session, tenant_id=tenant.id, ordinal=i
        )
        db_insights.append(insight)

    insight_manager = InsightManager(db_session)

    insight_to_be_archived = db_insights[1]
    insight_to_be_archived_name = insight_to_be_archived.name
    assert insight_to_be_archived.archived_at is None

    assert await insight_manager.archive(
        id=insight_to_be_archived.id, tenant_id=tenant.id
    )

    await db_session.refresh(insight_to_be_archived)
    assert insight_to_be_archived.archived_at
    assert insight_to_be_archived.ordinal == -1

    await db_session.refresh(db_insights[0])
    assert not db_insights[0].archived_at
    assert db_insights[0].ordinal == 1

    new_insight = await insight_manager.create(
        CreateInsightInput(
            name=insight_to_be_archived_name,
            url="https://dummy.insight.com/abc",
            description="test_description",
        ),
        tenant_id=tenant.id,
    )
    assert new_insight
    assert new_insight.name == insight_to_be_archived_name

    # if we try to create again it should fail with duplicate key error
    with pytest.raises(DuplicateKeyException) as e:
        await insight_manager.create(
            CreateInsightInput(
                name=insight_to_be_archived_name,
                url="https://dummy.insight.com/abc",
                description="test_description",
            ),
            tenant_id=tenant.id,
        )

    assert (
        e.value.args[0]
        == "Insight with same name already exists. Please give a unique name"
    )
    # if we try to update also with same name it should fail with duplicate key error
    with pytest.raises(DuplicateKeyException) as e1:
        await insight_manager.update(
            id=db_insights[2].id,
            input=UpdateInsightInput(name=insight_to_be_archived_name),
            tenant_id=tenant.id,
        )

    assert (
        e1.value.args[0]
        == "Insight with same name already exists. Please give a unique name"
    )


async def reorder_insights_for_test(
    tenant: Tenant, insight_manager: InsightManager
) -> None:
    await create_10_insights(tenant, insight_manager)

    insights = await insight_manager.get_all(tenant.id)
    assert len(insights) == 10

    count = 10
    for insight in insights:
        assert insight.ordinal == count
        count -= 1

    reordered_insight_ids = [
        insights[5].id,  # test5
        insights[6].id,  # test4
        insights[7].id,  # test3
        insights[8].id,  # test2
        insights[9].id,  # test1
        insights[4].id,  # test6
        insights[3].id,  # test7
        insights[2].id,  # test8
        insights[1].id,  # test9
        insights[0].id,  # test10
    ]
    await insight_manager.reorder(reordered_insight_ids, tenant.id)


async def create_10_insights(tenant: Tenant, insight_manager: InsightManager) -> None:
    for i in range(1, 11):
        insight = await insight_manager.create(
            CreateInsightInput(
                name=f"test{i}",
                url="https://dummy.insight.com/abc1",
                description="test_description",
            ),
            tenant_id=tenant.id,
        )
        assert insight
        assert insight.ordinal == i
