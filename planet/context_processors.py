# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.sites.models import Site

from planet.forms import SearchForm
from planet.settings import PLANET_CONFIG


def context(request):
    if request.method == "GET" and request.GET.get("search"):
        search_form = SearchForm(request.GET)
    else:
        search_form = SearchForm()

    site = Site.objects.get(pk=settings.SITE_ID)

    return {"site": site, "SITE_NAME": site.name,
        "search_form": search_form, "PLANET_CONFIG": PLANET_CONFIG}
