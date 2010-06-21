# -*- coding: utf-8 -*-
"""
"""

from django.conf.urls.defaults import patterns, url


# HTML view's urls
urlpatterns = patterns('planet.views',
    url(r'^blogs/(?P<blog_id>\d+)/$', "blog_detail", name="blog_detail"),
    url(r'^blogs/$', "blogs_list", name="blogs_list"),

    url(r'^feeds/(?P<feed_id>\d+)/tags/(?P<tag>.*)/$', "feed_detail", name="by_tag_feed_detail"),
    url(r'^feeds/(?P<feed_id>\d+)/$', "feed_detail", name="feed_detail"),
    url(r'^feeds/$', "feeds_list", name="feeds_list"),

    url(r'^authors/(?P<author_id>\d+)/tags/(?P<tag>.*)/$', "author_detail", name="by_tag_author_detail"),
    url(r'^authors/(?P<author_id>\d+)/$', "author_detail", name="author_detail"),
    url(r'^authors/$', "authors_list", name="authors_list"),
    
    url(r'^tags/(?P<tag>.*)/feeds/$', "tag_feeds_list", name="tag_feeds_list"),
    url(r'^tags/(?P<tag>.*)/authors/$', "tag_authors_list", name="tag_authors_list"),
    url(r'^tags/(?P<tag>.*)/$', "tag_detail", name="tag_detail"),
    url(r'^tags/$', "tags_cloud", name="tags_cloud"),
    
    url(r'^opml/$', "opml", name="opml"),
    url(r'^foaf/$', "foaf", name="foaf"),
    
    url(r'^posts/(?P<post_id>\d+)/$', "post_detail", name="post_detail"),
    url(r'^posts/$', "posts_list", name="posts_list"),
    
    url(r'^search/$', "search", name="planet_search"),

    url(r'^$', "index", name="planet_index"),
)

# Feed's urls
urlpatterns += patterns('planet.feeds',
    url(r'^posts/feeds/rss/$', "rss_feed", name="rss_feed"),
    url(r'^feeds/rss/tags/(?P<tag>.*)/$', "rss_feed", name="tag_rss_feed"),
    url(r'^feeds/rss/authors/(?P<author_id>\d+)/$', "rss_feed", name="author_rss_feed"),
    url(r'^feeds/rss/authors/(?P<author_id>\d+)/tags/(?P<tag>.*)/$', "rss_feed", name="tag_author_rss_feed"),
)
