# -*- coding: utf-8 -*-
"""
"""

from django import forms
from django.utils.translation import gettext as _


SEARCH_CHOICES = (
    ("posts", _("Posts")),
    ("blogs", _("Blogs")),
    ("authors", _("Authors")),
    ("feeds", _("Feeds")),
)


class SearchForm(forms.Form):
    w = forms.ChoiceField(choices=SEARCH_CHOICES, label="")
    q = forms.CharField(max_length=100, label="")
