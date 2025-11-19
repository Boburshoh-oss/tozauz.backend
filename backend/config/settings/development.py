from config.settings.base import *
import os


DEBUG = bool(os.getenv("DEBUG"))
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": os.getenv("DB_HOSTNAME", "db"),
        "NAME": os.getenv("DB_NAME", "tozauz"),
        "USER": os.getenv("DB_USERNAME", "tozauz"),
        "PASSWORD": os.getenv("DB_PASSWORD", "tozauz"),
        "PORT": int(os.getenv("DB_PORT", "5432")),
    }
}

STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "../", "staticfiles")

if DEBUG:
    MIDDLEWARE += [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ]
    # INSTALLED_APPS += [
    #     "debug_toolbar",
    # ]
    import socket

    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[:-1] + "1" for ip in ips] + ["127.0.0.1"]
    # INTERNAL_IPS = [
    #     # ...
    #     "127.0.0.1",
    #     "localhost",
    #     "localhost:8000/",
    #     "localhost:8000",
    #     "http://localhost:8000",
    #     "0.0.0.0:8000",
    #     # ...
    # ]

    # this is the main reason for not showing up the toolbar
    import mimetypes

    mimetypes.add_type("application/javascript", ".js", True)

    DEBUG_TOOLBAR_CONFIG = {
        "INTERCEPT_REDIRECTS": False,
    }


