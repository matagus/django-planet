import uuid
import factory
from django.utils import timezone

from factory.fuzzy import FuzzyDateTime, FuzzyText
from factory.django import DjangoModelFactory

from planet.models import Blog, Feed, Post, PostAuthorData, Author


class BlogFactory(DjangoModelFactory):
    class Meta:
        model = Blog

    title = factory.Sequence(lambda n: f"blog-{n}")
    url = factory.LazyAttribute(lambda obj: f"http://{obj.title}.blogspot.com/")


class FeedFactory(DjangoModelFactory):
    class Meta:
        model = Feed

    guid = factory.LazyFunction(uuid.uuid4)
    title = factory.Sequence(lambda n: f"Feed-{n}")
    blog = factory.SubFactory(BlogFactory)
    url = factory.LazyAttribute(lambda obj: f"{obj.blog.url}feed-{obj.title}.rss")
    language = "en"


class AuthorFactory(DjangoModelFactory):
    class Meta:
        model = Author

    name = factory.Sequence(lambda n: f"Author #{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.name}@gmail.com")


class PostFactory(DjangoModelFactory):
    class Meta:
        model = Post

    title = factory.Sequence(lambda n: f"Post Title #{n}")
    feed = factory.SubFactory(FeedFactory)
    url = factory.LazyAttribute(lambda obj: f"post-{obj.feed.blog.url}.html")
    guid = factory.Sequence(lambda n: f"GUID-{n}")
    content = FuzzyText(length=200)
    date_published = FuzzyDateTime(timezone.now())

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
