import uuid

from sqlalchemy import text
from sqlmodel import col, select

from worker_safety_service.models import AsyncSession, Configuration

configs_to_store = (
    {
        "id": uuid.uuid4(),
        "name": "APP.TEMPLATE_FORM.LABELS",
        "value": '{"key": "templateForm", "label": "Template Form", "labelPlural": "Template Forms"}',
    },
    {
        "id": uuid.uuid4(),
        "name": "APP.TEMPLATE_FORM.ATTRIBUTES",
        "value": '{"attributes": []}',
    },
)


async def downgrade(db_session: AsyncSession) -> None:
    delete_query = """
    DELETE FROM public.configurations WHERE name = :name and value = :value and tenant_id is null;
    """

    for config in configs_to_store:
        await db_session.execute(text(delete_query), config)

    for config in configs_to_store:
        await db_session.execute(text(delete_query), config)


async def test_migration(db_session: AsyncSession) -> None:
    # query config table and assert that "APP.TEMPLATE_FORM.LABELS", "APP.TEMPLATE_FORM.ATTRIBUTES" are present
    configs = (
        await db_session.exec(
            select(Configuration).where(
                col(Configuration.name).in_(
                    ["APP.TEMPLATE_FORM.LABELS", "APP.TEMPLATE_FORM.ATTRIBUTES"]
                ),
            )
        )
    ).all()

    assert configs

    # run migration
    await downgrade(db_session)

    # query config table and assert that "APP.TEMPLATE_FORM.LABELS", "APP.TEMPLATE_FORM.ATTRIBUTES" are not present
    new_configs = (
        await db_session.exec(
            select(Configuration).where(
                col(Configuration.name).in_(
                    ["APP.TEMPLATE_FORM.LABELS", "APP.TEMPLATE_FORM.ATTRIBUTES"]
                ),
            )
        )
    ).all()

    assert not new_configs
