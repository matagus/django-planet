# -*- coding: utf-8 -*-

from django.utils import feedgenerator
from django.utils.cache import patch_vary_headers
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.template import Context, loader, RequestContext
from django.db.models import Count, Max
from django.utils.translation import ugettext_lazy as _

from planet.models import Feed, Author, Post
from planet.forms import SearchForm

from tagging.models import Tag


def authors_list(request):
    authors = Author.site_objects.all()

    return render_to_response("authors/list.html",
        {"authors_list": authors},
        context_instance=RequestContext(request))

def author_detail(request, author_id, tag=None):
    author = get_object_or_404(Author, pk=author_id)
    
    params_dict = {"feed__author": author}
    
    if tag:
        tag = get_object_or_404(Tag, name=tag)
        params_dict.update({"tags": tag})
        
    posts = Post.site_objects.filter(**params_dict).order_by("-date_created")
    
    return render_to_response("authors/show.html",
        {"author": author, "posts": posts, "tag": tag},
        context_instance=RequestContext(request))

def feeds_list(request):
    feeds_list = Feed.site_objects.all()

    return render_to_response("feeds/list.html", {"feeds_list": feeds_list},
        context_instance=RequestContext(request))

def feed_detail(request, feed_id, tag=None):
    feed = get_object_or_404(Feed, pk=feed_id)
    
    params_dict = {"feed": feed}
    
    if tag:
        tag = get_object_or_404(Tag, name=tag)
        params_dict.update({"tags": tag})
        
    posts = Post.site_objects.filter(**params_dict).order_by("-date_created")
    
    return render_to_response("feeds/show.html",
        {"feed": feed, "posts": posts, "tag": tag},
        context_instance=RequestContext(request))

def posts_list(request):
    posts = Post.site_objects.all().order_by("-date_created")
    
    return render_to_response("posts/list.html", {"posts": posts},
        context_instance=RequestContext(request))

def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    
    return render_to_response("posts/show.html", {"post": post},
        context_instance=RequestContext(request))

def tag_detail(request, tag):
    tag = get_object_or_404(Tag, name=tag)
        
    posts = Post.site_objects.filter(tags=tag).order_by("-date_created")
    
    return render_to_response("tags/show.html", {"posts": posts, "tag": tag},
        context_instance=RequestContext(request))

def tag_authors_list(request, tag):
    tag = get_object_or_404(Tag, name=tag)
    
    authors = Author.site_objects.filter(feed__post__tags__name=tag).distinct()
    
    return render_to_response("authors/list_for_tag.html",
        {"authors": authors, "tag": tag},
        context_instance=RequestContext(request))

def tag_feeds_list(request, tag):
    tag = get_object_or_404(Tag, name=tag)
    
    feeds_list = Feed.site_objects.filter(post__tags__name=tag).distinct()
    
    return render_to_response("feeds/list_for_tag.html",
        {"feeds_list": feeds_list, "tag": tag},
        context_instance=RequestContext(request))

def tags_cloud(request, min_posts_count=1):
    max_posts_count = Tag.objects.annotate(count=Count("post")
        ).filter(count__gt=min_posts_count, name__isnull=False).aggregate(Max("count"))
    max_posts_count = max_posts_count["count__max"]
    
    tags_cloud = Tag.objects.annotate(count=Count("post")
        ).filter(count__gt=min_posts_count, name__isnull=False).order_by("name")

    return render_to_response("tags/cloud.html",
        {"tags_cloud": tags_cloud, "max_posts_count": max_posts_count},
        context_instance=RequestContext(request))

def foaf(request):
    feeds = Feed.site_objects.all()
    
    return render_to_response("microformats/foaf.xml", {"feeds": feeds},
        context_instance=RequestContext(request), mimetype="text/xml")

def opml(request):
    feeds = Feed.site_objects.all()
    
    return render_to_response("microformats/opml.xml", {"feeds": feeds},
        context_instance=RequestContext(request), mimetype="text/xml")

def search(request):
    if request.method == "GET" and request.GET.get("search") == "go":
        search_form = SearchForm(request.GET)

        if search_form.is_valid():
            query = search_form.cleaned_data["q"]
            
            if search_form.cleaned_data["w"] == "posts":
                params_dict = {"title__icontains": query}
            
                posts = Post.site_objects.filter(**params_dict
                    ).distinct().order_by("-date_created")
            
                return render_to_response("posts/list.html", {"posts": posts},
                    context_instance=RequestContext(request))
            
            elif search_form.cleaned_data["w"] == "tags":
                params_dict = {"name__icontains": query}

                tags_list = Tag.objects.filter(**params_dict
                    ).distinct().order_by("name")

                return render_to_response("tags/list.html",
                    {"tags_list": tags_list},
                    context_instance=RequestContext(request))

            elif search_form.cleaned_data["w"] == "blogs":
                params_dict = {"name__icontains": query}

                feeds_list = Feed.site_objects.filter(**params_dict
                    ).order_by("name")

                return render_to_response("feeds/list.html",
                    {"feeds_list": feeds_list},
                    context_instance=RequestContext(request))

            elif search_form.cleaned_data["w"] == "authors":
                params_dict = {"name__icontains": query}

                authors_list = Author.site_objects.filter(**params_dict
                    ).order_by("name")

                return render_to_response("authors/list.html",
                    {"authors_list": authors_list},
                    context_instance=RequestContext(request))

            else:
                return HttpResponseRedirect(reverse("posts_list"))

        else:
            return HttpResponseRedirect(reverse("posts_list"))

    else:
        return HttpResponseRedirect(reverse("posts_list"))