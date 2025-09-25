# django-planet

![Python Compatibility](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue.svg) [![PyPi Version](https://img.shields.io/pypi/v/django-planet.svg)](https://pypi.python.org/pypi/django-planet)  ![CI badge](https://github.com/matagus/django-planet/actions/workflows/ci.yml/badge.svg) [![codecov](https://codecov.io/gh/matagus/django-planet/graph/badge.svg?token=a64SxEDQk0)](https://codecov.io/gh/matagus/django-planet) [![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

A Django app that provides everything you need to build planet feed aggregator website.

**WARNING**: Latest changes are backward incompatible with previous versions. I'm working in a new, minimal version compatible w/ latest Django and Python versions.

Features
========

- ...

Installation
============

Via `pip` command:

```bash
pip install django-planet
```

...or you can clone the repo and install it using `pip` too:

```bash
git clone git://github.com/matagus/django-planet.git
cd django-planet
pip install -e .
```

then add `planet` to your `settings.py`:

```python
INSTALLED_APPS = (
    # ...
    "planet",
)
```

then run the migrations:

```bash
python manage.py migrate
```

Usage
=====

TO-DO

Screenshots
===========

Post List
---------

![Post List](https://raw.githubusercontent.com/matagus/django-planet/main/screenshots/post-list.png)

Blog View
---------

![Blog View](https://raw.githubusercontent.com/matagus/django-planet/main/screenshots/blog.png)

Author View
-----------

![Author View](https://raw.githubusercontent.com/matagus/django-planet/main/screenshots/blog.png)

Full Post View
--------------

![Full Post View](https://raw.githubusercontent.com/matagus/django-planet/main/screenshots/full-post.png)


DEMO
----

* [django-planet.matagus.dev](https://django-planet.matagus.dev/)

Code for the demo site is available at the `project/` directory.

Contributing
============

Contributions are welcome! ❤️

Please read [Contributing.md](CONTRIBUTING.md) for detailed instructions on how to help.

Running Tests
-------------

`hatch run test:test` will run the tests in every Python + Django versions combination.

`hatch run test.py3.12-5.0:test will run them for python 3.12 and Django 5.0. Please see possible combinations using
`hatch env show` ("test" matrix).


License
=======

`django-planet` is released under an BSD License - see the `LICENSE` file
for more information.


Acknowledgements
================

Develop & built using [![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch) [![linting - Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff) [![code style - black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
