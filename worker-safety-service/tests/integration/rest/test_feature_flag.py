import json
import os
from logging import getLogger
from typing import Callable
from unittest.mock import patch

import pytest
from httpx import AsyncClient

from tests.factories import FeatureFlagFactory, TenantFactory
from worker_safety_service.config import Settings
from worker_safety_service.models import AsyncSession
from worker_safety_service.rest.routers.feature_flag import (
    FeatureFlagAttributes,
    FeatureFlagRequest,
)

logger = getLogger(__name__)
FEATURE_FLAGS_ROUTE = "http://127.0.0.1:8000/rest/feature-flags"

feature_names = [
    "test_jsb",
    "test_ebo",
    "test_work_packages",
    "test_forms_list",
    "test_insights",
    "test_daily_summary",
    "test_dashboard",
]

default_mock_feature_flags_from_ld = {
    "test_work_packages": True,
    "test_forms_list": True,
    "test_insights": True,
    "test_jsb": True,
    "test_daily_summary": True,
    "test_dashboard": True,
    "test_ebo": True,
    "test_ebo_drop_down_menu": True,
    "test_ebo_button": True,
    "test_jsb_drop_down_menu": True,
    "test_jsb_button": True,
    "test_work_packages_tab": True,
    "test_forms_list_tab": True,
    "test_forms_list_add_test_jsb_button": True,
    "test_insights_tab": True,
    "test_daily_summary_tab": True,
    "test_dashboard_tab": True,
}

mocked_path = "worker_safety_service.dal.feature_flag.FeatureFlagManager._get_ld_flags"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_feature_flag_201_ok(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    feature_flag_request = FeatureFlagRequest.pack(
        attributes=FeatureFlagAttributes(
            feature_name="TEST_EBO_REST_API",
            configurations={
                "component1": True,
                "component2": False,
                "component3": True,
            },
        )
    )
    response = await client.post(
        FEATURE_FLAGS_ROUTE,
        json=json.loads(feature_flag_request.json()),
    )
    assert response.status_code == 201
    feature_flag = response.json()["data"]["attributes"]

    assert feature_flag["feature_name"] == "TEST_EBO_REST_API"
    assert feature_flag["configurations"] == {
        "component1": True,
        "component2": False,
        "component3": True,
    }


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_feature_flag_200_ok(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    db_feature_flags = await FeatureFlagFactory.persist_many(db_session, size=3)
    assert len(db_feature_flags) == 3

    flag_to_update = db_feature_flags[0]
    assert flag_to_update.configurations == {
        "component1": True,
        "component2": False,
        "component3": True,
    }

    feature_flag_request = FeatureFlagRequest.pack(
        attributes=FeatureFlagAttributes(
            configurations={"component2": True, "component4": True, "component5": False}
        )
    )
    response = await client.put(
        f"{FEATURE_FLAGS_ROUTE}/{flag_to_update.feature_name}",
        json=json.loads(feature_flag_request.json()),
    )
    assert response.status_code == 200
    feature_flag = response.json()["data"]["attributes"]

    assert feature_flag["feature_name"] == flag_to_update.feature_name
    assert feature_flag["configurations"] == {
        "component1": True,
        "component2": True,
        "component3": True,
        "component4": True,
        "component5": False,
    }


@pytest.mark.skip(reason="code not being used anywhere for now.")
@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_feature_flag_200_ok_with_db_configs(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    flags = [
        "test_projects",
        "test_forms",
        "test_insights",
        "test_jsb",
        "test_daily_summary",
        "test_dashboard",
    ]
    for flag in flags:
        await FeatureFlagFactory.persist(db_session, feature_name=flag)

    flag_names = "&".join(f"filter[featureName]={flag}" for flag in flags[:3])
    mocked_path = "worker_safety_service.launch_darkly.launch_darkly_client.LaunchDarklyClient.get_all_tenant_flags"

    # all flags enabled in LD
    with patch(
        mocked_path,
        return_value={
            "test_projects": True,
            "test_forms": True,
            "test_insights": True,
            "test_jsb": True,
            "test_daily_summary": True,
            "test_dashboard": True,
        },
    ):
        response = await client.get(f"{FEATURE_FLAGS_ROUTE}?{flag_names}")

        assert response.status_code == 200
        feature_flags = response.json()["data"]
        assert {ff["attributes"]["feature_name"] for ff in feature_flags} == set(
            flags[:3]
        )
        for ff in feature_flags:
            assert ff["attributes"]["configurations"] == {
                "component1": True,
                "component2": False,
                "component3": True,
            }

    # few flags disabled in LD
    with patch(
        mocked_path,
        return_value={
            "test_projects": False,
            "test_forms": False,
            "test_insights": True,
            "test_jsb": True,
            "test_daily_summary": True,
            "test_dashboard": True,
        },
    ):
        response = await client.get(f"{FEATURE_FLAGS_ROUTE}?{flag_names}")

        assert response.status_code == 200
        feature_flags = response.json()["data"]
        assert {ff["attributes"]["feature_name"] for ff in feature_flags} == set(
            flags[:3]
        )
        for ff in feature_flags:
            if ff["attributes"]["feature_name"] not in ["test_projects", "test_forms"]:
                assert ff["attributes"]["configurations"] == {
                    "component1": True,
                    "component2": False,
                    "component3": True,
                }
            else:
                assert ff["attributes"]["configurations"] == {}

    # with few flags missing from feature_flag table
    with patch(
        mocked_path,
        return_value={
            "test_projects": False,
            "test_forms": True,
            "test_insights": True,
            "test_jsb": True,
            "test_daily_summary": True,
            "test_dashboard": True,
        },
    ):
        flag_names = "&".join(
            f"filter[featureName]={flag}"
            for flag in ["random_flag_1", "test_jsb", "test_forms"]
        )
        response = await client.get(f"{FEATURE_FLAGS_ROUTE}?{flag_names}")

        assert response.status_code == 200
        feature_flags = response.json()["data"]
        assert {ff["attributes"]["feature_name"] for ff in feature_flags} == {
            "random_flag_1",
            "test_jsb",
            "test_forms",
        }
        for ff in feature_flags:
            if ff["attributes"]["feature_name"] in ["test_jsb", "test_forms"]:
                assert ff["attributes"]["configurations"] == {
                    "component1": True,
                    "component2": False,
                    "component3": True,
                }
            else:
                assert ff["attributes"]["configurations"] == {}

    # with ALL flags missing from feature_flag table
    with patch(
        mocked_path,
        return_value={
            "test_projects": False,
            "test_forms": False,
            "test_insights": True,
            "test_jsb": True,
            "test_daily_summary": True,
            "test_dashboard": True,
        },
    ):
        flag_names = "&".join(
            f"filter[featureName]={flag}" for flag in ["random_flag_1", "random_flag_2"]
        )
        response = await client.get(f"{FEATURE_FLAGS_ROUTE}?{flag_names}")

        assert response.status_code == 200
        feature_flags = response.json()["data"]
        assert {ff["attributes"]["feature_name"] for ff in feature_flags} == {
            "random_flag_1",
            "random_flag_2",
        }
        for ff in feature_flags:
            assert ff["attributes"]["configurations"] == {}


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_feature_flag_200_ok_with_all_flags_enabled_in_ld(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)

    flag_names = "&".join(f"filter[featureName]={flag}" for flag in feature_names[:4])

    # all flags enabled in LD
    with patch(mocked_path, return_value=default_mock_feature_flags_from_ld):
        response = await client.get(f"{FEATURE_FLAGS_ROUTE}?{flag_names}")

        assert response.status_code == 200
        feature_flags = response.json()["data"]
        assert {ff["attributes"]["feature_name"] for ff in feature_flags} == set(
            feature_names[:4]
        )
        for ff in feature_flags:
            if ff["attributes"]["feature_name"] == "test_jsb":
                assert ff["attributes"]["configurations"] == {
                    "test_jsb_drop_down_menu": True,
                    "test_jsb_button": True,
                }
            elif ff["attributes"]["feature_name"] == "test_ebo":
                assert ff["attributes"]["configurations"] == {
                    "test_ebo_drop_down_menu": True,
                    "test_ebo_button": True,
                }
            elif ff["attributes"]["feature_name"] == "test_forms_list":
                assert ff["attributes"]["configurations"] == {
                    "test_forms_list_tab": True,
                    "test_forms_list_add_test_jsb_button": True,
                }
            else:
                assert ff["attributes"]["configurations"] == {
                    "test_work_packages_tab": True
                }


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_feature_flag_200_ok_with_few_flags_disabled_in_ld(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)

    mock_feature_flags_from_ld_with_false_flags = {
        "test_work_packages": True,
        "test_forms": True,
        "test_insights": True,
        "test_jsb": False,
        "test_daily_summary": True,
        "test_dashboard": True,
        "test_ebo": True,
        "test_ebo_drop_down_menu": True,
        "test_ebo_button": True,
        "test_jsb_drop_down_menu": True,
        "test_jsb_button": True,
        "test_work_packages_tab": True,
        "test_forms_list_tab": True,
        "test_forms_list_add_test_jsb_button": True,
        "test_insights_tab": True,
        "test_daily_summary_tab": True,
        "test_dashboard_tab": True,
    }

    flag_names = "&".join(f"filter[featureName]={flag}" for flag in feature_names[:3])

    # few flags disabled in LD
    with patch(mocked_path, return_value=mock_feature_flags_from_ld_with_false_flags):
        response = await client.get(f"{FEATURE_FLAGS_ROUTE}?{flag_names}")

        assert response.status_code == 200
        feature_flags = response.json()["data"]
        assert {ff["attributes"]["feature_name"] for ff in feature_flags} == set(
            feature_names[:3]
        )
        for ff in feature_flags:
            if ff["attributes"]["feature_name"] == "test_jsb":
                assert ff["attributes"]["configurations"] == {}
            elif ff["attributes"]["feature_name"] == "test_ebo":
                assert ff["attributes"]["configurations"] == {
                    "test_ebo_drop_down_menu": True,
                    "test_ebo_button": True,
                }
            else:
                assert ff["attributes"]["configurations"] == {
                    "test_work_packages_tab": True
                }


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_feature_flag_200_ok_with_few_missing_flags_in_ld(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)

    flags = {"missing_flag_1", "test_jsb", "test_ebo"}
    flag_names = "&".join(f"filter[featureName]={flag}" for flag in flags)

    # with few flags missing from feature_flag table
    with patch(mocked_path, return_value=default_mock_feature_flags_from_ld):
        response = await client.get(f"{FEATURE_FLAGS_ROUTE}?{flag_names}")

        assert response.status_code == 200
        feature_flags = response.json()["data"]
        assert {ff["attributes"]["feature_name"] for ff in feature_flags} == flags
        for ff in feature_flags:
            if ff["attributes"]["feature_name"] == "test_jsb":
                assert ff["attributes"]["configurations"] == {
                    "test_jsb_drop_down_menu": True,
                    "test_jsb_button": True,
                }
            elif ff["attributes"]["feature_name"] == "test_ebo":
                assert ff["attributes"]["configurations"] == {
                    "test_ebo_drop_down_menu": True,
                    "test_ebo_button": True,
                }
            else:
                assert ff["attributes"]["configurations"] == {}


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_feature_flag_200_ok_with_random_flags_in_ld(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    flags = {"random_flag_1", "random_flag_2"}
    flag_names = "&".join(f"filter[featureName]={flag}" for flag in flags)

    # with ALL flags missing from feature_flag table
    with patch(mocked_path, return_value=default_mock_feature_flags_from_ld):
        response = await client.get(f"{FEATURE_FLAGS_ROUTE}?{flag_names}")

        assert response.status_code == 200
        feature_flags = response.json()["data"]
        assert {ff["attributes"]["feature_name"] for ff in feature_flags} == flags
        for ff in feature_flags:
            assert ff["attributes"]["configurations"] == {}


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_mobile_key(rest_client: Callable[..., AsyncClient]) -> None:
    os.environ["LAUNCH_DARKLY_MOBILE_KEY"] = "mocked_sdk_key"
    settings = Settings()
    client = rest_client()
    with patch("worker_safety_service.rest.routers.feature_flag.settings", settings):
        response = await client.get(f"{FEATURE_FLAGS_ROUTE}/mobile-key")

        assert response.status_code == 200
        assert response.json() == "mocked_sdk_key"
