import enum
import logging

logger = logging.getLogger(__name__)


@enum.unique
class Permission(enum.Enum):
    VIEW_ALL_CWF = "VIEW_ALL_CWF"
    CREATE_CWF = "CREATE_CWF"
    EDIT_DELETE_OWN_CWF = "EDIT_DELETE_OWN_CWF"
    EDIT_DELETE_ALL_CWF = "EDIT_DELETE_ALL_CWF"
    REOPEN_OWN_CWF = "REOPEN_OWN_CWF"
    REOPEN_ALL_CWF = "REOPEN_ALL_CWF"
    CONFIGURE_CUSTOM_TEMPLATES = "CONFIGURE_CUSTOM_TEMPLATES"
    ALLOW_EDITS_AFTER_EDIT_PERIOD = "ALLOW_EDITS_AFTER_EDIT_PERIOD"


permissions_viewer = [Permission.VIEW_ALL_CWF]
permissions_supervisor = permissions_viewer + [
    Permission.CREATE_CWF,
    Permission.EDIT_DELETE_OWN_CWF,
    Permission.REOPEN_OWN_CWF,
]
permissions_manager = permissions_supervisor + [
    Permission.EDIT_DELETE_ALL_CWF,
    Permission.REOPEN_ALL_CWF,
]
permissions_administrator = permissions_manager + [
    Permission.CONFIGURE_CUSTOM_TEMPLATES
]


role_to_permissions_map = {
    "viewer": permissions_viewer,
    "supervisor": permissions_supervisor,
    "manager": permissions_manager,
    "administrator": permissions_administrator,
}
