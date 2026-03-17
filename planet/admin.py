from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from planet.models import Blog, Feed, Post, Author, PostAuthorData


@admin.register(PostAuthorData)
class PostAuthorDataAdmin(admin.ModelAdmin):
    list_display = ("get_author_name", "is_contributor", "post")
    list_filter = ("is_contributor", "author")

    def get_author_name(self, obj):
        return obj.author.name

    get_author_name.short_description = "Author Name"


class FeedInlineReadOnly(admin.TabularInline):
    model = Feed
    fields = ("feed_link",)
    readonly_fields = ("feed_link",)
    extra = 0
    can_delete = False

    def feed_link(self, obj):
        url = reverse("admin:planet_feed_change", args=[obj.id])
        return format_html('<a href="{}">{}</a>', url, obj.title)

    feed_link.short_description = "Feed"

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    list_display = ("title", "url", "blog", "language", "etag", "last_modified", "last_checked", "is_active")
    list_filter = ("language",)
    list_select_related = ("blog",)
    search_fields = ["title", "url", "blog__title"]
    readonly_fields = ("authors_list",)
    fieldsets = (
        (None, {"fields": ("title", "url", "blog", "language")}),
        ("Feed Status", {"fields": ("etag", "last_modified", "last_checked", "is_active")}),
        ("Authors", {"fields": ("authors_list",)}),
    )

    def authors_list(self, obj):
        if not obj.pk:
            return "-"
        authors = Author.objects.filter(postauthordata__post__feed=obj).distinct().order_by("name")
        if not authors.exists():
            return "No authors"
        links = [
            format_html(
                '<a href="{}">{}</a>',
                reverse("admin:planet_author_change", args=[author.id]),
                author.name,
            )
            for author in authors
        ]
        return format_html("<br>".join(f"{link}" for link in links))

    authors_list.short_description = "Authors"


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("name", "email")
    search_fields = ["name"]
    readonly_fields = ("feeds_list",)
    fieldsets = (
        (None, {"fields": ("name", "email", "profile_url")}),
        ("Feeds", {"fields": ("feeds_list",)}),
    )

    def feeds_list(self, obj):
        if not obj.pk:
            return "-"
        feeds = Feed.objects.filter(post__postauthordata__author=obj).distinct().order_by("title")
        if not feeds.exists():
            return "No feeds"
        links = [
            format_html(
                '<a href="{}">{}</a>',
                reverse("admin:planet_feed_change", args=[feed.id]),
                feed.title,
            )
            for feed in feeds
        ]
        return format_html("<br>".join(f"{link}" for link in links))

    feeds_list.short_description = "Feeds"


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "feed", "guid", "date_published", "date_created")
    list_filter = ("feed__title", "language")
    list_select_related = ("feed", "feed__blog")
    search_fields = ["title", "feed__blog__title"]


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ("title", "url", "date_created")
    search_fields = ["title", "url"]
    inlines = [FeedInlineReadOnly]
