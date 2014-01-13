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
    author_email="me@matagus.com.ar",

    install_requires=["feedparser", "south", "django-tagging>=0.3.1",
        "django-pagination", "Django>=1.4", "BeautifulSoup",
        "pinax-theme-bootstrap==3.0a4"],

    packages=find_packages(),
    package_dir={"planet": "planet"},
    package_data={
        "planet": [
            "static/planet/*.css",
            "static/planet/images/*.png",
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
        "Programming Language :: Python :: 2.6",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary",
    ],
    zip_safe=False,
)
