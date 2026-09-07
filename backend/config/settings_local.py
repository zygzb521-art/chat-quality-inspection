# Local development settings
# Usage: DJANGO_SETTINGS_MODULE=config.settings_local python manage.py ...
# Or: cp config/settings_local.example.py config/settings_local.py

from .settings import *

DEBUG = True
ALLOWED_HOSTS = ['*']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
CELERY_TASK_ALWAYS_EAGER = True
CORS_ALLOW_ALL_ORIGINS = True