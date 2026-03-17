from django import forms
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from planet.models import Blog, Feed, Post, Author, PostAuthorData


class AddFeedByURLForm(forms.ModelForm):
    class Meta:
        model = Feed
        fields = ["url"]

    def clean_url(self):
        url = self.cleaned_data["url"]
        if Feed.objects.filter(url=url).exists():
            raise forms.ValidationError(_("A feed with this URL already exists."))
        return url


@admin.register(PostAuthorData)
class PostAuthorDataAdmin(admin.ModelAdmin):
    list_display = ("get_author_name", "is_contributor", "post")
    list_filter = ("is_contributor", "author")

    def get_author_name(self, obj):
        return obj.author.name

    get_author_name.short_description = _("Author Name")


class FeedInlineReadOnly(admin.TabularInline):
    model = Feed
    fields = ("feed_link",)
    readonly_fields = ("feed_link",)
    extra = 0
    can_delete = False

    def feed_link(self, obj):
        url = reverse("admin:planet_feed_change", args=[obj.id])
        return format_html('<a href="{}">{}</a>', url, obj.title)

    feed_link.short_description = _("Feed")

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
        (_("Feed Status"), {"fields": ("etag", "last_modified", "last_checked", "is_active")}),
        (_("Authors"), {"fields": ("authors_list",)}),
    )

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            return AddFeedByURLForm
        return super().get_form(request, obj, **kwargs)

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return [(None, {"fields": ["url"]})]
        return super().get_fieldsets(request, obj)

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return []
        return super().get_readonly_fields(request, obj)

    def save_model(self, request, obj, form, change):
        if not change:
            url = form.cleaned_data["url"]
            blog, _ = Blog.objects.get_or_create_stub(url)
            feed = Feed.objects.create_stub(url, blog)
            obj.pk = feed.pk
            return
        super().save_model(request, obj, form, change)

    def authors_list(self, obj):
        if not obj.pk:
            return "-"
        authors = Author.objects.filter(postauthordata__post__feed=obj).distinct().order_by("name")
        if not authors.exists():
            return _("No authors")
        links = [
            format_html(
                '<a href="{}">{}</a>',
                reverse("admin:planet_author_change", args=[author.id]),
                author.name,
            )
            for author in authors
        ]
        return format_html("<br>".join(f"{link}" for link in links))

    authors_list.short_description = _("Authors")


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("name", "email")
    search_fields = ["name"]
    readonly_fields = ("feeds_list",)
    fieldsets = (
        (None, {"fields": ("name", "email", "profile_url")}),
        (_("Feeds"), {"fields": ("feeds_list",)}),
    )

    def feeds_list(self, obj):
        if not obj.pk:
            return "-"
        feeds = Feed.objects.filter(post__postauthordata__author=obj).distinct().order_by("title")
        if not feeds.exists():
            return _("No feeds")
        links = [
            format_html(
                '<a href="{}">{}</a>',
                reverse("admin:planet_feed_change", args=[feed.id]),
                feed.title,
            )
            for feed in feeds
        ]
        return format_html("<br>".join(f"{link}" for link in links))

    feeds_list.short_description = _("Feeds")


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
