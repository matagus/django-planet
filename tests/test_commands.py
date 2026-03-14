from django.test import TestCase

from planet.models import Author, Feed, Post, PostAuthorData
from tests.factories import PostFactory


class CreateAuthorsForPostTest(TestCase):
    def test_creates_author_and_link(self):
        post = PostFactory()
        Post.objects.create_authors_for_post(post, [{"name": "Jane Doe"}])
        self.assertEqual(PostAuthorData.objects.filter(post=post).count(), 1)
        self.assertTrue(Author.objects.filter(name="Jane Doe").exists())

    def test_skips_missing_name_key(self):
        post = PostFactory()
        Post.objects.create_authors_for_post(post, [{"email": "x@example.com"}])
        self.assertEqual(PostAuthorData.objects.filter(post=post).count(), 0)

    def test_skips_empty_name(self):
        post = PostFactory()
        Post.objects.create_authors_for_post(post, [{"name": "   "}])
        self.assertEqual(PostAuthorData.objects.filter(post=post).count(), 0)

    def test_handles_empty_authors_list(self):
        post = PostFactory()
        Post.objects.create_authors_for_post(post, [])
        self.assertEqual(PostAuthorData.objects.filter(post=post).count(), 0)

    def test_deduplicates_authors_via_get_or_create(self):
        post = PostFactory()
        Post.objects.create_authors_for_post(post, [{"name": "Alice"}, {"name": "Alice"}])
        self.assertEqual(Author.objects.filter(name="Alice").count(), 1)


class FeedModelDeadCodeRemovedTest(TestCase):
    def test_no_should_update_method(self):
        self.assertFalse(hasattr(Feed, "should_update"))

    def test_no_retrieve_and_update_method(self):
        self.assertFalse(hasattr(Feed, "retrieve_and_update"))
