# -*- coding: utf-8 -*-
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect

from planet.models import Blog, Feed, Author, Post
from planet.forms import SearchForm


def index(request):
    posts = Post.objects.all()
    return render(request, "planet/posts/list.html", {"posts": posts})


def blog_list(request, query=None):
    if query is None:
        blogs_list = Blog.objects.all()
    else:
        blogs_list = Blog.objects.search(query)

    return render(
        request, "planet/blogs/list.html", {"blogs_list": blogs_list}
    )


def blog_detail(request, blog_id, slug=None):
    blog = get_object_or_404(Blog, pk=blog_id)

    if slug is None:
        return redirect(blog, permanent=True)

    posts = Post.objects.for_blog(blog)\
        .select_related("feed", "feed__blog").prefetch_related("authors")

    return render(
        request, "planet/blogs/detail.html", {"blog": blog, "posts": posts}
    )


def feed_list(request, query=None):
    if query is None:
        feed_list = Feed.objects.all().select_related('blog')
    else:
        feed_list = Feed.objects.search(query)

    return render(
        request, "planet/feeds/list.html", {"feeds_list": feed_list}
    )


def feed_detail(request, feed_id, tag=None, slug=None):
    feed = get_object_or_404(Feed.objects.select_related('blog'), pk=feed_id)

    if not slug:
        return redirect(feed, permanent=True)

    posts = Post.objects.for_feed(feed)\
        .select_related("feed", "feed__blog").prefetch_related("authors")

    return render(
        request, "planet/feeds/detail.html", {"feed": feed, "posts": posts}
    )


def author_list(request, query=None):
    if query is not None:
        authors = Author.objects.search(query)
    else:
        authors = Author.objects.all()

    return render(
        request, "planet/authors/list.html", {"authors_list": authors}
    )


def author_detail(request, author_id, tag=None, slug=None):
    author = get_object_or_404(Author, pk=author_id)

    if not slug:
        return redirect(author, permanent=True)

    posts = Post.objects.for_author(author)\
        .select_related("feed", "feed__blog").prefetch_related("authors")

    return render(
        request, "planet/authors/detail.html",
        {"author": author, "posts": posts}
    )


def post_list(request, query=None):
    if query is None:
        posts = Post.objects
    else:
        posts = Post.objects.search(query)

    return render(
        request, "planet/posts/list.html",
        {
            "posts": posts.select_related("feed", "feed__blog").prefetch_related("authors")
        }
    )


def post_detail(request, post_id, slug=None):
    post = get_object_or_404(
        Post.objects.select_related("feed", "feed__blog")
            .prefetch_related("authors"),
        pk=post_id
    )

    if not slug:
        return redirect(post, permanent=True)

    return render(request, "planet/posts/detail.html", {"post": post})


def search(request):
    if request.method == "GET":
        search_form = SearchForm(request.GET)

        if search_form.is_valid():
            query = search_form.cleaned_data["q"]
            search_what = search_form.cleaned_data["w"]

            if search_what == "posts":
                return post_list(request, query)

            elif search_what == "blogs":
                return blog_list(request, query)

            elif search_what == "feeds":
                return feed_list(request, query)

            elif search_what == "authors":
                return author_list(request, query)

    return HttpResponseRedirect(reverse("planet:post-list"))
