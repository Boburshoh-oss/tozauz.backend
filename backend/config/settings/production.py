import os
from config.settings.base import *
from decouple import config
DEBUG = bool(config("DEBUG"))
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

# CRONJOBS = [
#     ('* * * * *', 'django.core.management.call_command', ['user-check'])
# ]

# sentry_sdk.init(
#     dsn="https://071a71402d10d6a1602ab6ee990eaa0b@o4506508436439040.ingest.sentry.io/4506508444696576",
#     # Set traces_sample_rate to 1.0 to capture 100%
#     # of transactions for performance monitoring.
#     traces_sample_rate=1.0,
#     # Set profiles_sample_rate to 1.0 to profile 100%
#     # of sampled transactions.
#     # We recommend adjusting this value in production.
#     profiles_sample_rate=1.0,
# )