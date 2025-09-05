"""Borrowed from lens: https://github.com/urbint/lens/blob/main/support/docker/superset/superset_config.py
"""

# Full superset configuration file:
# https://github.com/apache/superset/blob/master/superset/config.py

import logging
import os

from celery.schedules import crontab  # type: ignore

# from flask_appbuilder.security.manager import AUTH_DB
#
# from custom_security_manager import CustomSecurityManager
#
logger = logging.getLogger(__name__)

# should never be set in staging/production
LOCAL_DEV = os.environ.get("LOCAL_DEV", False)
if LOCAL_DEV:
    logger.warn("Running in LOCAL_DEV mode - never do this in Prod!")

################################################################################
# Superset Misc
################################################################################

# supports encrypting values sent into queries, if needed
SECRET_KEY = os.environ.get("SUPERSET_SECRET_KEY")

# Whether to run the web server in debug mode or not
DEBUG = os.environ.get("FLASK_ENV") == "development"
FLASK_USE_RELOAD = True

MAPBOX_API_KEY = os.environ.get("MAPBOX_API_KEY")

# date format fix
# https://superset.apache.org/docs/installation/configuring-superset
SIP_15_ENABLED = True

# Do not show user 'info' or 'profile' links in the menu
# MENU_HIDE_USER_INFO = True

################################################################################
# Superset metadata db (stores users, dashboards, roles, etc)
################################################################################

SQLALCHEMY_DATABASE_URI = os.environ.get("SUPERSET_DB")
SQLALCHEMY_CUSTOM_PASSWORD_STORE = None
SQLALCHEMY_TRACK_MODIFICATIONS = False

################################################################################
# Query constants/limits
################################################################################

ROW_LIMIT = 10000
VIZ_ROW_LIMIT = 10000
SAMPLES_ROW_LIMIT = 1000
FILTER_SELECT_ROW_LIMIT = 10000
QUERY_SEARCH_LIMIT = 1000

# max rows for csvs
# SQL_MAX_ROW = 10000

################################################################################
# Superset Webserver
################################################################################

# Should be lower than your [load balancer / proxy / envoy / kong / ...] timeout
# settings. You should also make sure to configure your WSGI server (gunicorn,
# nginx, apache, ...) timeout setting to be <= to this setting
SUPERSET_WEBSERVER_TIMEOUT = 60

################################################################################
# Superset Frontend
################################################################################

# These 2 settings are used by dashboard period force refresh feature
# When user choose auto force refresh frequency
# < SUPERSET_DASHBOARD_PERIODICAL_REFRESH_LIMIT
# they will see warning message in the Refresh Interval Modal.
SUPERSET_DASHBOARD_PERIODICAL_REFRESH_LIMIT = 0
SUPERSET_DASHBOARD_PERIODICAL_REFRESH_WARNING_MESSAGE = None
SUPERSET_DASHBOARD_POSITION_DATA_LIMIT = 65535

################################################################################
# HTTP and routing
################################################################################

# HTTP_HEADERS = {"X-Frame-Options": "ALLOWALL"}
# ENABLE_CORS = True
# CORS_OPTIONS = {
#     "supports_credentials": True,
#     "allow_headers": ["*"],
#     "resources": [
#         "/superset/csrf_token/",  # auth
#     ],
# }

# used b/c we're forwarding across a load balancer (in kubernetes)
# https://superset.apache.org/docs/installation/configuring-superset
ENABLE_PROXY_FIX = True

################################################################################
# White label details
################################################################################

# hide the default icon
APP_ICON_WIDTH = 0

# Specify where clicking the logo would take the user
# e.g. setting it to '/' would take the user to '/superset/welcome/'
LOGO_TARGET_PATH = None
# Specify tooltip that should appear when hovering over the App Icon/Logo
LOGO_TOOLTIP = ""
# Specify any text that should appear to the right of the logo
LOGO_RIGHT_TEXT = ""

# shown in the 'add database' dropdown
PREFERRED_DATABASES = ["PostgreSQL"]

################################################################################
# Sessions
################################################################################

# Flask session cookie options
# See https://flask.palletsprojects.com/en/1.1.x/security/#set-cookie-options
SESSION_COOKIE_HTTPONLY = True  # Prevent cookie from being read by frontend JS?
# Prevent cookie from being transmitted over non-tls?
# `false` in local dev for local sessions, but should be True in production
SESSION_COOKIE_SECURE = False if LOCAL_DEV else True
SESSION_COOKIE_SAMESITE = (
    None if LOCAL_DEV else "None"
)  # One of [None, 'None', 'Lax', 'Strict']

# Flask-WTF flag for CSRF
WTF_CSRF_ENABLED = False if LOCAL_DEV else True

# Add endpoints that need to be exempt from CSRF protection
# WTF_CSRF_EXEMPT_LIST = ["superset.views.core.log", "superset.charts.api.data"]

################################################################################
# Auth, Roles, and Permissions
################################################################################

# AUTH_TYPE = AUTH_DB
# AUTH_ROLE_ADMIN = "Admin"

# noisy, but can be useful for debugging permissions issues
# SILENCE_FAB = True
# # SILENCE_FAB = False
# FAB_ADD_SECURITY_VIEWS = True
# FAB_ADD_SECURITY_PERMISSION_VIEW = False
# FAB_ADD_SECURITY_VIEW_MENU_VIEW = False
# FAB_ADD_SECURITY_PERMISSION_VIEWS_VIEW = False
#
# CUSTOM_SECURITY_MANAGER = CustomSecurityManager

################################################################################
# Celery config
################################################################################

REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = os.environ.get("REDIS_PORT", "6379")
REDIS_DB = os.environ.get("REDIS_DB", "0")
# can use either the 3 args above, or the full REDIS_URL var
REDIS_URL = os.environ.get(
    "REDIS_URL", "redis://%s:%s/%s" % (REDIS_HOST, REDIS_PORT, REDIS_DB)
)


class CeleryConfig:
    # set a different database here (not `0`)
    BROKER_URL = REDIS_URL
    CELERY_IMPORTS = (
        "superset.sql_lab",
        "superset.tasks",
        "superset.tasks.thumbnails",
    )
    CELERY_RESULT_BACKEND = REDIS_URL
    CELERYD_PREFETCH_MULTIPLIER = 10
    CELERY_ACKS_LATE = True
    CELERY_ANNOTATIONS = {
        "sql_lab.get_sql_results": {
            "rate_limit": "100/s",
        },
        "email_reports.send": {
            "rate_limit": "1/s",
            "time_limit": 600,
            "soft_time_limit": 600,
            "ignore_result": True,
        },
    }
    CELERYBEAT_SCHEDULE = {
        "reports.scheduler": {
            "task": "reports.scheduler",
            "schedule": crontab(minute="*", hour="*"),
        },
        "reports.prune_log": {
            "task": "reports.prune_log",
            "schedule": crontab(minute=0, hour=0),
        },
    }


CELERY_CONFIG = CeleryConfig

################################################################################
# Email, Alerts, Reports
################################################################################

# https://superset.apache.org/docs/installation/alerts-reports
# FEATURE_FLAGS = {"ALERT_REPORTS": True}

SCREENSHOT_LOCATE_WAIT = 100
SCREENSHOT_LOAD_WAIT = 600

# Email configuration
EMAIL_NOTIFICATIONS = True
SMTP_HOST = os.environ.get("SMTP_HOST", "mailhog")
SMTP_PORT = os.environ.get("SMTP_PORT", "1025")
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
SMTP_STARTTLS = os.environ.get("SMTP_USE_TLS", "False") == "True"
SMTP_SSL = os.environ.get("SMTP_USE_SSL", "False") == "True"

SMTP_MAIL_FROM = os.environ.get(
    "DEFAULT_FROM_EMAIL", "Urbint Support <support@urbint.com>"
)

# This is for internal use, you can keep http. This should resolve to the web
# facing superset instance.
WEBDRIVER_BASEURL = os.environ.get("SUPERSET_SERVICE_BASEURL", "http://superset:8090")

# This is the link sent to the recipient, change to your domain eg. https://superset.mydomain.com
WEBDRIVER_BASEURL_USER_FRIENDLY = os.environ.get(
    "SUPERSET_EXTERNAL_BASEURL", "http://reports.local.urbinternal.com:8090"
)

# A user with access to the dashboards
# The user with this username is passed to superset's MachineAuthProvider
THUMBNAIL_SELENIUM_USER = os.environ.get(
    "MACHINE_USER", "admin@email.local.urbinternal.com"
)
