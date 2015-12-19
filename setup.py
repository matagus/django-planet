# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="django-planet",
    version=__import__("planet").__version__,
    url="http://github.com/matagus/django-planet",
    license="BSD",
    description="Django app to build a planet, RSS/Atom feeds aggregator.",
    long_description=open("docs/usage.rst").read(),

    author="Matias Agustin Mendez",
    author_email="matagus+planet@gmail.com",

    install_requires=[
        "feedparser",
        "django-tagging==0.3.6",
        "django-pagination-py3",
        "Django>=1.6",
        "beautifulsoup4"
    ],

    packages=find_packages(),
    package_dir={"planet": "planet"},
    package_data={
        "planet": [
            "static/planet/*.css",
            "static/planet/images/*.png",
            "locale/*/LC_MESSAGES/*.mo",
            "templates/*.html",
            "templates/planet/*.html",
            "templates/planet/*/*.html",
            "templates/planet/authors/blocks/*.html",
            "templates/planet/tags/blocks/*.html",
            "templates/planet/feeds/blocks/*.html",
            "templates/planet/microformats/*.xml",
        ]},

    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary",
    ],
    zip_safe=False,
)
