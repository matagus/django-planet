# -*- coding: utf-8 -*-

from django.contrib import admin

from planet.models import (Blog, Generator, Feed, FeedLink, Post, PostLink,
    Author, PostAuthorData, Enclosure)

for model in (Blog, Generator, Feed, FeedLink, Post, PostLink, Author,
        PostAuthorData, Enclosure):
    admin.site.register(model)

