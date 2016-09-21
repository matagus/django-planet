Usage
=====

Changing your settings.py
-------------------------

Modifiy your projects ``settings.py`` file following the next steps:

1. Check your ``INSTALLED_APPS``:

.. code-block:: python

  INSTALLED_APPS = (
    # django required contrib apps
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    # 3rd-party required apps:
    'pagination',
    'tagging',
    'pinax_theme_bootstrap',
    # and finally:
    'planet',
  )

2. Configure your database. Here is an example using mysql:

.. code-block:: python

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': 'planet',                      # Or path to database file if using sqlite3.
            'USER': '<myuser>',                      # Not used with sqlite3.
            'PASSWORD': '<mypass>',                  # Not used with sqlite3.
            'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
            'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
        }
    }

3. Choose a site id:

.. code-block:: python

  SITE_ID = 1

4. For Django 1.8 include the following context processors:

.. code-block:: python

	TEMPLATES = [
	    {
	        'BACKEND': 'django.template.backends.django.DjangoTemplates',
	        'DIRS': [
	            '/path/to/project/templates',
	        ],
	        'APP_DIRS': True,
	        'OPTIONS': {
	            'context_processors': [
	                'django.template.context_processors.debug',
	                'django.template.context_processors.request',
	                'django.contrib.auth.context_processors.auth',
	                'django.contrib.messages.context_processors.messages',
					'django.template.context_processors.i18n',
					'django.template.context_processors.media',
					'django.template.context_processors.static',
					'django.template.context_processors.tz',
	                'planet.context_processors.context',
	            ],
	        },
	    },
	]

If you're still using Django 1.6.x or 1.7.x, then set `TEMPLATE_CONTEXT_PROCESSORS`
this way:

.. code-block:: python

    TEMPLATE_CONTEXT_PROCESSORS = (
        'django.contrib.auth.context_processors.auth',
        'django.core.context_processors.debug',
        'django.core.context_processors.i18n',
        'django.core.context_processors.media',
        'django.core.context_processors.static',
        'django.core.context_processors.tz',
        'django.core.context_processors.request',
        'django.contrib.messages.context_processors.messages',
        'planet.context_processors.context',
    )

5. Check your middlewares to include:

.. code-block:: python

    MIDDLEWARE_CLASSES = (
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'pagination.middleware.PaginationMiddleware',
    )

Please do not forget ``pagination.middleware.PaginationMiddleware`` middleware!

5. Add planet configuration variables:

.. code-block:: python

    PLANET = {
        "USER_AGENT": "My Planet/1.0",
    }

6. Properly configure your static files root directory:

.. code-block:: python

   STATIC_URL = '/static/'

7. Only for Django 1.6.x or 1.7.x set your projects templates root directory:

.. code-block:: python

    TEMPLATE_DIRS = (
        '/path/to/project/templates',
        # other paths...
    )

and your template loaders:

.. code-block:: python

    TEMPLATE_LOADERS = (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
        # some other template loaders here...
    )

8. Finally in your project's templates directory create a ``site_base.html``
   template if you don't already have one:

.. code-block:: html

    {% extends "base.html" %}


9. Optionally, modify cookie names so you don't have login conflicts with other
   projects:

.. code-block:: python

    LANGUAGE_COOKIE_NAME = "myplanetlng"
    SESSION_COOKIE_NAME = "myplanetid"

Congratulations! Your settings are complete. Now you'll need to change other
files in order to get a running project.

Enable planet urls
------------------

1. Add the planet urls include to your project's ``urls.py`` (remember to
   also include admin urls so you can use the admin to manage your planet!):

.. code-block:: python

    from django.conf.urls import patterns, include, url

    from django.contrib import admin
    admin.autodiscover()

    urlpatterns = patterns('',
        url(r'^', include('planet.urls')),
        url(r'^admin/', include(admin.site.urls)),
        # ... other url bits...
    )

Syncdb and add some feeds!
--------------------------

1. Then create the database structure::

     ./manage.py syncdb

2. Add some feeds::

    python manage.py planet_add_feed http://www.economonitor.com/feed/rss/
    python manage.py planet_add_feed http://www.ft.com/rss/home/us

3. And surely you'll want to add a cron entry to periodically update them all::

    30 * * * * python manage.py planet_update_all_feeds

This attempts to pull in new posts every 30 minutes.

4. Now you're done. Just run::

   ./manage.py runserver

and browse your planet at http://localhost:8000/ in your favorite browser!
