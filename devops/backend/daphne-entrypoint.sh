#!/bin/bash

# Apply database migrations
# python manage.py migrate

# Collect static files
# python manage.py collectstatic --noinput

# Start Daphne
daphne -b 0.0.0.0 -p 8000 config.asgi:application
