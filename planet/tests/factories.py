import factory

from factory.fuzzy import FuzzyText

from django.contrib.sites.models import Site

from planet.models import (
    Blog, Feed, Post, Generator, PostAuthorData,
    PostLink, Enclosure, FeedLink, Author, Category
)


class SiteFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Site

    domain = factory.Sequence(lambda n: u'example-site-{}.com'.format(n))


class BlogFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Blog

    title = factory.Sequence(lambda n: u'blog-{}'.format(n))
    url = factory.LazyAttribute(lambda obj: u'http://{}.blogspot.com/'.format(obj.title))


class GeneratorFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Generator

    name = factory.Sequence(lambda n: u'generator-{}'.format(n))


class CategoryFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Category

    title = factory.Sequence(lambda n: u'Category #{}'.format(n))


class FeedFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Feed

    title = factory.Sequence(lambda n: u'Feed-{}'.format(n))
    blog = factory.SubFactory(BlogFactory)
    url = factory.LazyAttribute(lambda obj: '{}feed-{}.rss'.format(obj.blog.url, obj.title))
    generator = factory.SubFactory(GeneratorFactory)
    language = "en"
    site = factory.SubFactory(SiteFactory)


class AuthorFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Author

    name = factory.Sequence(lambda n: u'Author #{}'.format(n))
    email = factory.LazyAttribute(lambda obj: u'{}@gmail.com'.format(obj.name))


class PostFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Post

    title = factory.Sequence(lambda n: u'Post Title #{}'.format(n))
    feed = factory.SubFactory(FeedFactory)
    url = factory.LazyAttribute(lambda obj: u'post-{}.html'.format(obj.feed.blog.url))
    guid = factory.Sequence(lambda n: u'GUID-{}'.format(n))
    content = FuzzyText(length=200)

    @factory.post_generation
    def authors(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for author in extracted:
                PostAuthorDataFactory.create(post=self, author=author)


class PostAuthorDataFactory(factory.DjangoModelFactory):
    FACTORY_FOR = PostAuthorData

    post = factory.SubFactory(PostFactory)
    author = factory.SubFactory(AuthorFactory)


class PostLinkFactory(factory.DjangoModelFactory):
    FACTORY_FOR = PostLink

    title = factory.Sequence(lambda n: u'post-link-{}'.format(n))
    post = factory.SubFactory(PostFactory)
    rel = "alternative"
    mime_type = "application/html"
    link = factory.LazyAttribute(lambda obj: u'{}post-links/{}.html'.format(obj.feed.blog.url, obj.title))


class FeedLinkFactory(factory.DjangoModelFactory):
    FACTORY_FOR = FeedLink

    feed = factory.SubFactory(FeedFactory)
    rel = "alternative"
    mime_type = "application/html"
    link = factory.LazyAttribute(lambda obj: u'{}feed-links/{}.rss'.format(obj.feed.blog.url, obj.feed.title))


class EnclosureFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Enclosure

    title = factory.Sequence(lambda n: u'enclosure-#{}'.format(n))
    post = factory.SubFactory(PostFactory)
    mime_type = "image/png"
    link = factory.Sequence(lambda obj: u'{}post-{}/image-{}.png'.format(obj.post.feed.blog.url, obj.post.title, obj.title))
    Length = 1024
