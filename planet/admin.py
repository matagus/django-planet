# -*- coding: utf-8 -*-

from django.contrib import admin

from planet.models import (Blog, Feed, Post, Author, PostAuthorData)


@admin.register(PostAuthorData)
class PostAuthorDataAdmin(admin.ModelAdmin):
    list_display = ("author", "is_contributor", "post")
    list_filter = ("is_contributor", "author")


@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    list_display = (
        "title", "url", "blog", "language", "etag", "last_modified", "last_checked", "is_active"
    )
    list_filter = ("language", )
    search_fields = ["title", "url", "blog__title"]


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("name", "email")
    search_fields = ["name"]


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "feed", "guid", "date_published", "date_created")
    list_filter = ("feed", "language")
    search_fields = ["title", "feed__blog__title"]


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ("title", "url", "date_created")
    search_fields = ["title", "url"]
