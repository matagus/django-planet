
DEBUG = True
TEMPLATE_DEBUG = True
INTERNAL_IPS = ["127.0.0.1"]

LANGUAGE_COOKIE_NAME = "planetlng"
SESSION_COOKIE_NAME = "planetid"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'planet.db',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

TIME_ZONE = 'America/BuenosAires'

USER_AGENT = "django-planet/0.1"

