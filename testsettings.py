import django

DEBUG = False
TEMPLATE_DEBUiG = DEBUG

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

INSTALLED_APPS = (
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'tagging',
    'planet',
)

SECRET_KEY = 'abcde12345'

SITE_ID = 1

if django.VERSION[:2] < (1, 6):
    # Since 1.6 version Django comes with discover_runner builtin!
    INSTALLED_APPS += ('discover_runner', )
    TEST_RUNNER = 'discover_runner.DiscoverRunner'

PLANET = {"USER_AGENT": "django-planet/0.1"}
