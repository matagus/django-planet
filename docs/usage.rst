=====
Usage
=====

This is a generic application for Django projects aiming to provide a planet
feed aggregator app.

Django-planet is heavily based on `Feedjack`_'s models by Gustavo Picon and my
django app that extends it: `feedjack-extension`_. Changes and addings to
models were inspired by Mark Pilgrim's `Feedparser`_.

.. _feedjack: http://www.feedjack.org/
.. _feedjack-extension: http://code.google.com/p/feedjack-extension/
.. _feedparser: http://www.feedparser.org/

Screenshots:
------------

The following screenshots are just for demonstration purposes:

.. image:: https://raw.github.com/matagus/django-planet/master/screenshots/latest-posts.png

.. image:: https://raw.github.com/matagus/django-planet/master/screenshots/post-view.png

.. image:: https://raw.github.com/matagus/django-planet/master/screenshots/tag-view.png

 
INSTALLATION
------------
In order to get django-planet working you must:

Create a local_settings.py file::

    DEBUG = False
    TEMPLATE_DEBUG = DEBUG

    LANGUAGE_COOKIE_NAME = "planetlng"
    SESSION_COOKIE_NAME = "planetid"

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

    TEMPLATE_CONTEXT_PROCESSORS = (
        ...
        'planet.context_processors.context',
    )

    TIME_ZONE = 'America/Chicago'

    PLANET = {
        "USER_AGENT": "django-planet/0.1",
    }

Then create the database structure::

     ./manage.py syncdb
     ./manage.py migrate planet

Add some feeds::

    ./manage.py planet_add_feed http://simonwillison.net/atom/tagged/django/ 
    ./manage.py planet_add_feed http://jannisleidel.com/cat/django/feed/atom/
    ./manage.py planet_add_feed http://andrewwilkinson.wordpress.com/tag/django/feed/
    ./manage.py planet_add_feed http://djangodose.com/everything/feed/
    ./manage.py planet_add_feed http://seeknuance.com/tag/django/feed/atom
    ./manage.py planet_add_feed http://www.willmcgugan.com/blog/tech/feeds/tag/django/

And surely you'll want to add a cron entry to periodically run::

    30 * * * * python manage.py planet_update_all_feeds

This attempts to pull for new posts every 30 minutes.
    
And finally run::

     ./manage.py runserver 

Browse ``http://localhost:8000/`` and enjoy it!

Demo Project
------------

There's a simple demo project live at `django-planet.herokuapp.com`_

.. _django-planet.herokuapp.com: http://django-planet.herokuapp.com/
