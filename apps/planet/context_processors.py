# -*- coding: utf-8 -*-

from django.conf import settings

from planet.models import Site, Link
from planet.forms import SearchForm

def context(request):
    if request.method == "GET" and request.GET.get("search"):
        search_form = SearchForm(request.GET)
    else:
        search_form = SearchForm()
    
    return {"site": Site.objects.get(pk=settings.SITE_ID),
        "links": Link.objects.all(),
        "search_form": search_form}

