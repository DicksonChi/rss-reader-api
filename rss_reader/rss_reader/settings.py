"""
Django settings for rss_reader project.

"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split('|')
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', '').split('|')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # packages
    'rest_framework',
    'knox',
    'django_extensions',
    'corsheaders',
    'rest_framework_swagger',
    # apps
    'users',
    'feeds',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PERMISSION_CLASSES': [],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'rss_reader.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ["{}/templates".format(BASE_DIR)],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

SPECTACULAR_SETTINGS = {
    'TITLE': 'RSS Reader API',
    'DESCRIPTION': 'Rss Reader Management API',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

WSGI_APPLICATION = 'rss_reader.wsgi.application'

AUTH_USER_MODEL = 'users.User'

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('DBNAME'),
        'USER': os.getenv('DBUSER'),
        'PASSWORD': os.getenv('DBPASSWORD'),
        'HOST': os.getenv('DBHOST'),
        'PORT': os.getenv('DBPORT'),
    },
}

REST_KNOX = {
    'SECURE_HASH_ALGORITHM': 'cryptography.hazmat.primitives.hashes.SHA512',
    'AUTH_TOKEN_CHARACTER_LENGTH': 64,
    'USER_SERIALIZER': 'knox.serializers.UserSerializer',
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static_root')

STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)


# File storage
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'


REDIS_ADDRESS = os.getenv('REDIS_ADDRESS')
REDIS_PORT = os.getenv('REDIS_PORT')
REDIS_URL = 'redis://{}:{}/0'.format(REDIS_ADDRESS, REDIS_PORT)
# REDIS_ADDRESS = os.getenv('REDIS_ADDRESS')
# REDIS_PORT = os.getenv('REDIS_PORT')
# REDIS_URL = '{}://localhost:{}'.format(REDIS_ADDRESS, REDIS_PORT)

# CELERY
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 3600, 'fanout_prefix': True, 'fanout_patterns': True}  # 1 hour

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {'CLIENT_CLASS': 'django_redis.client.DefaultClient'},
    }
}
