.. django-planet documentation master file, created by
   sphinx-quickstart on Sun Jan 12 14:07:23 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to django-planet!
=========================

.. image:: _static/screenshots/latest-posts.png

This is a generic application for Django that allows you to quickly build a
planet aggregating RSS and ATOM feeds of your favorite blogs.

Some parts of this help docs has been copied from `django-tastypie`_ and then
readapted to django-planet. Kudos to `django-tastypie`_ for its docs!

.. _`django-tastypie`: http://groups.google.com/toastdriven/django-tastypie/

Content:
--------

.. toctree::
  :maxdepth: 1

  usage
  screenshots
  demo

  who_uses
  contributing


Getting Help
============

There are two primary ways of getting help. We have a `mailing list`_ hosted at
Google (https://groups.google.com/forum/#!forum/django-planet) or you may contact us
via email to matagus at gmail dot com. You may also `open an issue`_ in our
github repository (it requires you to have a github account).

.. _`mailing list`: https://groups.google.com/forum/#!forum/django-planet
.. _`open an issue`: https://github.com/matagus/django-planet/issues/


Requirements
============

django-planet requires the following modules but simply installing it
using Pip_ will also install them. Just type::

    pip install django-planet

Required
--------

* Python 3.4+ or 2.7+
* Django 1.6 or 1.7 or 1.8
* django-tagging 0.3.6
* django-pagination 1.0.0+ for python 2.7 or django-pagination-py3 for python 3.5
* feedparser >= 5.0
* pinax-theme-bootstrap >= 3.0
* BeautifulSoup4 >= 4.0

Optionally, install celery if you want to add and update feeds using async &
parallel tasks:

* Celery >= 3.0
* django-celery >= 3.0

Optional
--------

* south (only required if you're using Dajngo 1.6.x)

.. _Pip: http://pip.openplans.org/


Why django-planet?
=============

There are other feed aggregators out there for Django. You need to assess
the options available and decide for yourself. That said, here are some
common reasons for django-planet.

* You need to quickly create a blog aggregator website with a nice look & feel.
* You want a full website for browsing blog posts and its authors and tags,
  feeds and blogs.
* SEO matters to you: django-planet has templates with SEO metatags and it
  includes sitemaps so you may submit them to your favorite search engines.
* You want searching posts, blogs, tags and authors.
* You need to customize templates and have a rich set of template tags to do it.
* You want complete ATOM & RSS support

Running The Tests
=================

The easiest way to get setup to run django-planet's tests looks like::

  $ git clone https://github.com/matagus/django-planet.git
  $ cd django-planet
  $ virtualenv env
  $ . env/bin/activate
  $ ./env/bin/pip install -U -r requirements.txt
  $ ./env/bin/pip install -U mock django-discover-runner factory-boy tox

Then running the tests is as simple as::

  # From the same directory as above:
  $ tox

That will test django-planet using Python 2.7 combinated with Django 1.4,
Django 1.5 and Django 1.6.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
