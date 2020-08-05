# Environment variable overrides for local development
set FLASK_APP app.py
set FLASK_DEBUG 1
set FLASK_ENV development
set GUNICORN_WORKERS 1
set LOG_LEVEL debug
set SECRET_KEY not-so-secret