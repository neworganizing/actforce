import dj_database_url
from os import environ
from sys import exc_info

from unipath import FSPath as Path

# Helper lambda for gracefully degrading env variables. Taken from http://rdegges.com/devops-django-part-3-the-heroku-way
env = lambda e, d: environ[e] if environ.has_key(e) else d

DEFAULT_ORG_ID = '0014000000Wl0RfAAJ'
DEFAULT_ORG_NAME = 'Individual'

# Google Aanalytics Information
GA_ID = env('GA_ID', None)
GA_DOMAIN = env('SITE_DOMAIN', None)

BASE = Path(__file__).absolute().ancestor(2)
APP = Path(__file__).absolute().ancestor(1)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

if 'ADMIN_EMAIL' in environ and 'ADMIN_NAME' in environ:
    admin_name = environ['ADMIN_NAME']
    admin_email = environ['ADMIN_EMAIL']
    ADMINS = (
        (admin_name,admin_email),
    )
else:
    ADMINS = ()


MANAGERS = ADMINS

DATABASES = {
    'default': dj_database_url.config(default='postgres://localhost'),
}

if environ.has_key('AK_DBUSER'):
    DATABASES['actionkit'] = {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': environ['AK_DBNAME'],
        'USER': environ['AK_DBUSER'],
        'PASSWORD': environ['AK_DBPASS'],
        'HOST': env('AK_DBSERVER','client-db.actionkit.com'),
        'PORT': '3306',
    }

# Allow any hosts
ALLOWED_HOSTS = ['*']

TIME_ZONE = 'America/New_York'

LANGUAGE_CODE = 'en-us'

SITE_ID = 1

USE_I18N = True
USE_L10N = True

USE_TZ = True

MEDIA_URL = '/media/'

if environ.has_key('AWS_STORAGE_BUCKET'):
    AWS_STORAGE_BUCKET_NAME = environ['AWS_STORAGE_BUCKET']
    AWS_ACCESS_KEY_ID = environ['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = environ['AWS_SECRET_ACCESS_KEY']
    STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
    S3_URL = 'https://%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
    STATIC_URL = S3_URL
    ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'
else:
    STATIC_URL = '/static/'

# Additional locations of static files
MEDIA_ROOT = BASE.child('media')
STATIC_ROOT = BASE.child('static')
STATICFILES_DIRS = (
    BASE.child('ui'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = env('SECRET_KEY', 'fawefawief123123bnqawf123j253blrq1231l23ubqwfawelu123')

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'actforce.apps.base.middleware.ForceSSL',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'actforce.apps.base.middleware.SalesforceMiddleware',
)

if 'FORCE_SSL' in environ:
    FORCE_SSL = True
else:
    FORCE_SSL = False

ROOT_URLCONF = 'actforce.urls'

WSGI_APPLICATION = 'actforce.wsgi.application'

TEMPLATE_DIRS = [APP.child('templates')]

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Enable Django Admin
    'django.contrib.admin',

    # Heroku Specific Apps Here
    'gunicorn',

    # 3rd Party
    'storages',
    'boto',
    'south',
    'social_auth',
    'django_fields',

    # 1st Party Apps
    'actforce.apps.base',
    'actforce.apps.mover'

)

DATABASE_ROUTERS = (
    'django_actionkit.connections.AKRouter',
)

CACHES = {
    'default': {
        'BACKEND': 'django_pylibmc.memcached.PyLibMCCache'
    }
}

AUTHENTICATION_BACKENDS = (
    'social_auth.backends.google.GoogleBackend',
    'django.contrib.auth.backends.ModelBackend',
)

GOOGLE_WHITE_LISTED_DOMAINS = ['neworganizing.com']

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login/google/'

# Expire Sessions On Browser Close
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# SMTP Server
if 'SMTP_USER' in environ and 'SMTP_PASSWORD' in environ and 'SMTP_SERVER' in environ:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = environ['SMTP_HOST']
    EMAIL_PORT = environ.get('SMTP_PORT','22')
    EMAIL_USE_TLS = environ.get('SMTP_USETLS',True)
    EMAIL_HOST_USER = environ['SMTP_USER']
    EMAIL_HOST_PASSWORD = environ['SMTP_PASSWORD']

SF_OAUTH_CLIENT_ID = env('SF_OAUTH_CLIENT_ID', None)
SF_OAUTH_CLIENT_SECRET = env('SF_OAUTH_CLIENT_SECRET', None)
SF_OAUTH_REDIRECT_URI = env('SF_OAUTH_REDIRECT_URI',None)


# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# Import from localsettings
try:
    from actforce.localsettings import *
except ImportError:
    pass