""" Django settings for core project. """

import dj_database_url, os
from pathlib import Path
from django_components import ComponentsSettings
from django.utils.translation import gettext_lazy as _
from core.adminsites.admin_namespace import AdminNamespace
from core.adminsites.unfold import AdminSiteUnfoldSettings
from core.config.logging import LoggingConfigBuilder
from core.config.storage import MediaStorageAdapterResolver, StaticStorageAdapterResolver

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-me-in-prod')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True').lower() in ('1', 'true', 'yes', 'on')

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
    if host.strip()
]

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        'CSRF_TRUSTED_ORIGINS',
        'http://localhost:8000,http://127.0.0.1:8000'
    ).split(',')
    if origin.strip()
]


# Application definition

MEDIA_STORAGE_CONFIG = MediaStorageAdapterResolver.build_config(BASE_DIR)
STATIC_STORAGE_CONFIG = StaticStorageAdapterResolver.build_config(BASE_DIR)

PROJECT_APPS = [
    'core',
    'accounts',
    'tenancy',
    'front',
]

PROJECT_EXTRA_APPS = list(dict.fromkeys(MEDIA_STORAGE_CONFIG.extra_apps + STATIC_STORAGE_CONFIG.extra_apps))

INSTALLED_APPS = [
    'unfold',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_components',
    *PROJECT_APPS,
    *PROJECT_EXTRA_APPS,
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    *STATIC_STORAGE_CONFIG.extra_middleware,
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'tenancy.middleware.active_tenant_middleware.ActiveTenantMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        # 'APP_DIRS': True,
        'OPTIONS': {
            'loaders': [(
                'django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                    'django_components.template_loader.Loader',
                ]
            )],
            'builtins': [
                'django_components.templatetags.component_tags',
            ],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DB_SCHEMA = os.environ.get('DB_SCHEMA', 'gea')

DATABASES = {
    'default': dj_database_url.parse(
        os.environ.get('DATABASE_URL', 'postgres://luscious:blue@localhost:5432/gea_trader_db'),
        conn_max_age=600,
    )
}

if 'postgresql' in DATABASES['default']['ENGINE']:
    DATABASES['default'].setdefault('OPTIONS', {})
    DATABASES['default']['OPTIONS']['options'] = f'-c search_path={DB_SCHEMA},public'


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'es'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

LANGUAGES = [
    ('es', _('Spanish')),
    ('en', _('English')),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]


# Email
# https://docs.djangoproject.com/en/5.2/topics/email/

EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', '127.0.0.1')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '1025'))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'False').lower() in ('1', 'true', 'yes', 'on')
EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL', 'False').lower() in ('1', 'true', 'yes', 'on')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@localhost')


# Celery
# https://docs.celeryq.dev/

REDIS_URL = os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/0')

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', REDIS_URL)
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', REDIS_URL)
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_TASK_ALWAYS_EAGER = os.environ.get('CELERY_TASK_ALWAYS_EAGER', 'False').lower() in ('1', 'true', 'yes', 'on')
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = USE_TZ


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = STATIC_STORAGE_CONFIG.static_url
STATIC_ROOT = STATIC_STORAGE_CONFIG.static_root
MEDIA_URL = MEDIA_STORAGE_CONFIG.media_url
MEDIA_ROOT = MEDIA_STORAGE_CONFIG.media_root
STORAGES = MEDIA_STORAGE_CONFIG.storages | STATIC_STORAGE_CONFIG.storages

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django_components.finders.ComponentsFileSystemFinder',
]


# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'accounts.UserModel'


# Logging Config

LOGGING = LoggingConfigBuilder.build(debug=DEBUG, project_apps=PROJECT_APPS)


# Unfold Settings

MASTER_ADMIN_UNFOLD = AdminSiteUnfoldSettings.for_namespace(AdminNamespace.MASTER).build()
OWNER_ADMIN_UNFOLD = AdminSiteUnfoldSettings.for_namespace(AdminNamespace.OWNER).build()


# Django Components

COMPONENTS = ComponentsSettings(
    dirs=[],
    app_dirs=[
        'components',
    ],
)
