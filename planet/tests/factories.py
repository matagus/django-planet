import factory

from factory.fuzzy import FuzzyText
from factory.django import DjangoModelFactory

from planet.models import Blog, Feed, Post, PostAuthorData, Author


class BlogFactory(DjangoModelFactory):
    class Meta:
        model = Blog

    title = factory.Sequence(lambda n: u'blog-{}'.format(n))
    url = factory.LazyAttribute(lambda obj: u'http://{}.blogspot.com/'.format(obj.title))
    owner = None


class FeedFactory(DjangoModelFactory):
    class Meta:
        model = Feed

    title = factory.Sequence(lambda n: u'Feed-{}'.format(n))
    blog = factory.SubFactory(BlogFactory)
    url = factory.LazyAttribute(lambda obj: '{}feed-{}.rss'.format(obj.blog.url, obj.title))
    language = "en"


class AuthorFactory(DjangoModelFactory):
    class Meta:
        model = Author

    name = factory.Sequence(lambda n: u'Author #{}'.format(n))
    email = factory.LazyAttribute(lambda obj: u'{}@gmail.com'.format(obj.name))


class PostFactory(DjangoModelFactory):
    class Meta:
        model = Post

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


class PostAuthorDataFactory(DjangoModelFactory):
    class Meta:
        model = PostAuthorData

    post = factory.SubFactory(PostFactory)
    author = factory.SubFactory(AuthorFactory)
