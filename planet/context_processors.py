# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.sites.models import Site

from planet.forms import SearchForm

def context(request):
    if request.method == "GET" and request.GET.get("search"):
        search_form = SearchForm(request.GET)
    else:
        search_form = SearchForm()
    
    return {"site": Site.objects.get(pk=settings.SITE_ID),
        "search_form": search_form}

