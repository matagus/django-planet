import django

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ROOT_URLCONF = "planet.urls"

TIME_ZONE = 'UTC'

LANGUAGE_COOKIE_NAME = "planetlng"
SESSION_COOKIE_NAME = "planetid"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}

INSTALLED_APPS = [
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'tagging',
    'pagination',
    'planet',
]

SECRET_KEY = 'abcde12345'

SITE_ID = 1

if django.VERSION[:2] < (1, 6):
    # Since 1.6 version Django comes with discover_runner builtin!
    INSTALLED_APPS += ('discover_runner', 'south')
    TEST_RUNNER = 'discover_runner.DiscoverRunner'

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.media",
    'django.core.context_processors.static',
    "django.core.context_processors.request",
    "django.core.context_processors.i18n",
    "django.contrib.messages.context_processors.messages",
    "planet.context_processors.context"
)

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'pagination.middleware.PaginationMiddleware',
)

STATIC_URL = '/static/'

PLANET = {"USER_AGENT": "django-planet/0.1"}
