# -*- coding: utf-8 -*-

"""
A nice example to make setup.py file can be found
at http://jacobian.org/writing/django-apps-with-buildout/
thanks to Jacob Kaplan-Moss.
"""

import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "django-planet",
    version = "0.1",
    url = 'http://github.com/matagus/django-planet',
    license = 'BSD',
    description = "Django app to build a planet, RSS/Atom feeds aggregator.",
    long_description = read('README'),

    author = 'Matias Agustin Mendez',
    author_email = 'me@matagus.com.ar',

    packages = find_packages(),
    package_data={
        'planet': [
            'templates/*.html',
            'templates/planet/*.html',
            'templates/planet/authors/*.html',
            'templates/planet/authors/blocks/*.html',
            'templates/planet/blogs/*.html',
            'templates/planet/posts/*.html',
            'templates/planet/tags/*.html',
            'templates/planet/tags/blocks/*.html',
            'templates/planet/feeds/*.html',
            'templates/planet/feeds/blocks/*.html',
            'templates/planet/microformats/*.xml',
            'media/planet/css/*.css',
            'media/planet/js/*.js',
            'media/planet/icons/*.gif',
            'media/planet/images/*.png',
        ]},

    install_requires = ['setuptools', 'django', 'feedparser', 
        'django-pagination', 'django-tagging'],

    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary',
    ]
)
