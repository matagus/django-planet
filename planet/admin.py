# -*- coding: utf-8 -*-

from django.contrib import admin

from planet.models import (Blog, Generator, Feed, FeedLink, Post, PostLink,
    Author, PostAuthorData, Enclosure, Category)


class PostLinkAdmin(admin.ModelAdmin):
    list_display = ("title", "rel", "mime_type", "post", "link")
    list_filter = ("rel", "mime_type")

admin.site.register(PostLink, PostLinkAdmin)


class PostAuthorDataAdmin(admin.ModelAdmin):
    list_display = ("author", "is_contributor", "post")
    list_filter = ("is_contributor", "author")

admin.site.register(PostAuthorData, PostAuthorDataAdmin)


class EnclosureAdmin(admin.ModelAdmin):
    list_display = ("post", "mime_type", "length", "link")
    list_filter = ("mime_type", )

admin.site.register(Enclosure, EnclosureAdmin)

class FeedAdmin(admin.ModelAdmin):
    list_display = ("title", "url", "blog", "language",
        "category", "etag", "last_modified", "last_checked", "is_active")
    list_filter = ("language", "generator", "category")
    search_fields = ["title", "url", "blog__title"]

admin.site.register(Feed, FeedAdmin)

class AuthorAdmin(admin.ModelAdmin):
    list_display = ("name", "email")
    search_fields = ["name"]

admin.site.register(Author, AuthorAdmin)

class EnclosureInline(admin.StackedInline):
    model = Enclosure
    extra = 0

class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "feed", "guid", "date_created", "date_modified")
    list_filter = ("feed", )
    search_fields = ["title", "feed__blog__title"]

admin.site.register(Post, PostAdmin, inlines=[EnclosureInline])


class BlogAdmin(admin.ModelAdmin):
    list_display = ("title", "url", "date_created")
    search_fields = ["title", "url"]

admin.site.register(Blog, BlogAdmin)


class GeneratorAdmin(admin.ModelAdmin):
    list_display = ("name", "version", "link")

admin.site.register(Generator, GeneratorAdmin)


class FeedLinkAdmin(admin.ModelAdmin):
    list_display = ("feed", "mime_type", "rel", "link")
    list_filter = ("mime_type", "rel")

admin.site.register(FeedLink, FeedLinkAdmin)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ("title", )
    search_fields = ["title"]

admin.site.register(Category, CategoryAdmin)
