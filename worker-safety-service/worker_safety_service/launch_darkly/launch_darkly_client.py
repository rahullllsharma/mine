import ldclient
from ldclient import Context, LDClient
from ldclient.config import Config

from worker_safety_service.urbint_logging import get_logger

logger = get_logger(__name__)


class LaunchDarklyClient:
    _instance: "LaunchDarklyClient | None" = None
    _client: LDClient | None = None

    def __new__(cls, sdk_key: str) -> "LaunchDarklyClient":
        """
        This is a singleton class. This method ensures that only one instance of this
        class is created. It also initializes the LaunchDarkly client with the SDK key.

        This is required because the LaunchDarkly client should only be initialized once.
        """
        if not cls._instance:
            logger.info(f"SDK-KEY --> {sdk_key}")
            cls._instance = super(LaunchDarklyClient, cls).__new__(cls)
            ldclient.set_config(Config(sdk_key))
            cls._instance._client = ldclient.get()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        cls._client = None
        cls._instance = None

    def get_all_tenant_flags(self, tenant_key: str) -> dict:
        context = Context.create(key=tenant_key, kind="tenant")
        assert self._client
        state = self._client.all_flags_state(context)
        flag_dict = state.to_json_dict()
        logger.info(f"LD flags --> {flag_dict}")
        return flag_dict
