import pytest

from migrations.fixtures.feature_flag_seed_data import data as ff_data
from worker_safety_service.dal.exceptions.entity_already_exists import (
    EntityAlreadyExistsException,
)
from worker_safety_service.dal.feature_flag import FeatureFlagManager
from worker_safety_service.models import (
    AsyncSession,
    FeatureFlagCreateInput,
    FeatureFlagLogType,
    FeatureFlagUpdateInput,
)
from worker_safety_service.urbint_logging import get_logger

logger = get_logger(__name__)

feature_flag_default_count = len(ff_data)


# Successfully creating an feature_flag
@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_feature_flag(db_session: AsyncSession) -> None:
    feature_flag_manager = FeatureFlagManager(db_session)
    feature_flags = await feature_flag_manager.get_all_feature_flags()
    assert len(feature_flags) == feature_flag_default_count

    new_feature_flag = await feature_flag_manager.create_feature_flag(
        FeatureFlagCreateInput(
            feature_name="EBO",
            configurations={
                "component1": True,
                "component2": False,
                "component3": True,
            },
        ),
    )
    assert new_feature_flag
    assert new_feature_flag.feature_name == "EBO"
    assert new_feature_flag.configurations == {
        "component1": True,
        "component2": False,
        "component3": True,
    }

    assert len(new_feature_flag.logs) == 1

    assert new_feature_flag.logs[0]
    assert new_feature_flag.logs[0].log_type == FeatureFlagLogType.CREATE
    assert new_feature_flag.logs[0].configurations == new_feature_flag.configurations

    feature_flags = await feature_flag_manager.get_all_feature_flags()
    assert len(feature_flags) == feature_flag_default_count + 1


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_feature_flag_with_empty_configurations(
    db_session: AsyncSession,
) -> None:
    feature_flag_manager = FeatureFlagManager(db_session)

    with pytest.raises(ValueError) as e:
        await feature_flag_manager.create_feature_flag(
            input=FeatureFlagCreateInput(
                feature_name="test",
                configurations={},
            ),
        )

    assert e.value.args[0][0].exc.args[0] == "Configurations cannot be empty"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_feature_flag_with_duplicate_feature_name(
    db_session: AsyncSession,
) -> None:
    feature_flag_manager = FeatureFlagManager(db_session)
    db_feature_flag = await feature_flag_manager.create_feature_flag(
        FeatureFlagCreateInput(
            feature_name="EBO4",
            configurations={
                "component1": True,
                "component2": False,
                "component3": True,
            },
        ),
    )
    assert db_feature_flag
    assert len(db_feature_flag.logs) == 1

    with pytest.raises(EntityAlreadyExistsException) as e:
        await feature_flag_manager.create_feature_flag(
            input=FeatureFlagCreateInput(
                feature_name=db_feature_flag.feature_name,
                configurations={
                    "component3": True,
                    "component5": False,
                },
            ),
        )

    assert e.value.args[0] == "An entity with the same: id already exists."
    await db_session.refresh(db_feature_flag)
    assert len(db_feature_flag.logs) == 1


# Successfully updating an feature_flag
@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_feature_flag(db_session: AsyncSession) -> None:
    feature_flag_manager = FeatureFlagManager(db_session)
    db_feature_flag = await feature_flag_manager.create_feature_flag(
        FeatureFlagCreateInput(
            feature_name="EBO1",
            configurations={
                "component1": True,
                "component2": False,
                "component3": True,
            },
        ),
    )
    assert db_feature_flag
    assert db_feature_flag.configurations == {
        "component1": True,
        "component2": False,
        "component3": True,
    }
    assert len(db_feature_flag.logs) == 1

    updated_feature_flag = await feature_flag_manager.update_feature_flag(
        feature_name=db_feature_flag.feature_name,
        input=FeatureFlagUpdateInput(
            configurations={
                "component2": True,
                "component4": True,
                "component5": False,
            },
        ),
    )
    assert updated_feature_flag
    assert updated_feature_flag.feature_name == db_feature_flag.feature_name
    assert updated_feature_flag.configurations == {
        "component1": True,
        "component2": True,
        "component3": True,
        "component4": True,
        "component5": False,
    }

    assert len(updated_feature_flag.logs) == 2
    log = sorted(
        updated_feature_flag.logs,
        key=lambda ff: ff.created_at,
        reverse=True,
    )[0]
    assert log
    assert log.log_type == FeatureFlagLogType.UPDATE
    assert log.configurations == updated_feature_flag.configurations


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_feature_flag_with_duplicate_configuration(
    db_session: AsyncSession,
) -> None:
    feature_flag_manager = FeatureFlagManager(db_session)
    db_feature_flag = await feature_flag_manager.create_feature_flag(
        FeatureFlagCreateInput(
            feature_name="EBO3",
            configurations={
                "component1": True,
                "component2": False,
                "component3": True,
            },
        ),
    )
    assert db_feature_flag
    assert db_feature_flag.configurations == {
        "component1": True,
        "component2": False,
        "component3": True,
    }
    assert len(db_feature_flag.logs) == 1

    await feature_flag_manager.update_feature_flag(
        feature_name=db_feature_flag.feature_name,
        input=FeatureFlagUpdateInput(
            configurations={
                "component3": False,
                "component5": False,
            },
        ),
    )

    await db_session.refresh(db_feature_flag)
    assert db_feature_flag.configurations == {
        "component1": True,
        "component2": False,
        "component3": False,
        "component5": False,
    }
    assert len(db_feature_flag.logs) == 2


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_feature_flag_with_empty_configurations(
    db_session: AsyncSession,
) -> None:
    feature_flag_manager = FeatureFlagManager(db_session)
    db_feature_flag = await feature_flag_manager.create_feature_flag(
        FeatureFlagCreateInput(
            feature_name="EBO5",
            configurations={
                "component1": True,
                "component2": False,
                "component3": True,
            },
        ),
    )
    assert db_feature_flag
    with pytest.raises(ValueError) as e:
        await feature_flag_manager.update_feature_flag(
            feature_name=db_feature_flag.feature_name,
            input=FeatureFlagUpdateInput(
                configurations={},
            ),
        )

    assert e.value.args[0][0].exc.args[0] == "Configurations cannot be empty"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_feature_flags(db_session: AsyncSession) -> None:
    feature_flag_manager = FeatureFlagManager(db_session)
    for name in ["EBO2", "EBO6", "EBO7", "EBO8"]:
        await feature_flag_manager.create_feature_flag(
            FeatureFlagCreateInput(
                feature_name=name,
                configurations={
                    "component1": True,
                    "component2": False,
                    "component3": True,
                },
            ),
        )

    flags = await feature_flag_manager.get_by_feature_names(["EBO6", "EBO7"])

    assert flags
    assert len(flags) == 2
    assert {flag.feature_name for flag in flags} == {"EBO6", "EBO7"}
