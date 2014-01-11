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
    'planet',
    'tagging',
)

SECRET_KEY = 'abcde12345'

SITE_ID = 1

PLANET = {"USER_AGENT": "django-planet/0.1"}
