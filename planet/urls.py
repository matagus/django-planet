from django.urls import path

from planet import views

app_name = "planet"

urlpatterns = [
    path("blogs/<int:blog_id>/<slug:slug>/", views.blog_detail, name="blog-detail"),
    path("blogs/<int:blog_id>/", views.blog_detail),
    path("blogs/", views.blog_list, name="blog-list"),
    path("feeds/<int:feed_id>/<slug:slug>/", views.feed_detail, name="feed-detail"),
    path("feeds/<int:feed_id>/", views.feed_detail),
    path("feeds/", views.feed_list, name="feed-list"),
    path("authors/<int:author_id>/<slug:slug>/", views.author_detail, name="author-detail"),
    path("authors/<int:author_id>/", views.author_detail),
    path("authors/", views.author_list, name="author-list"),
    path("posts/<int:post_id>/<slug:slug>/", views.post_detail, name="post-detail"),
    path("posts/<int:post_id>/", views.post_detail),
    path("posts/", views.post_list, name="post-list"),
    path("search/", views.search, name="search"),
    path("", views.index, name="index"),
]
