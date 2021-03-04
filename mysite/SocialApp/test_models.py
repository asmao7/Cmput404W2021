"""
Uses Django's TestCase subclass to run unit tests on our models.
This ensures each test is run inside a transaction to provide isolation.
"""
import uuid
from django.test import TestCase
from django.conf import settings
from .models import Author, PostCategory, Post, Comment

class TestCases(TestCase):
    """
    Class that contains all of our test cases. We do this since testing models
    often involves the interrelationships between them rather than simply
    unit testing Django's ORM
    """
    @classmethod
    def setUpTestData(cls):
        """
        Set up test data for the models.
        Will run once, and then run all of the test functions after.
        """
        # Set up two test authors
        cls.author_id_1 = uuid.uuid4()
        cls.author_host_1 = settings.HOST_NAME
        cls.author_display_name_1 = "Test Author 1"
        cls.author_github_1 = "github.com/testauthor1"
        author_1 = Author(id=cls.author_id_1, host=cls.author_host_1,
                          display_name=cls.author_display_name_1,
                          github=cls.author_github_1)
        author_1.save()

        cls.author_id_2 = uuid.uuid4()
        cls.author_host_2 = settings.HOST_NAME
        cls.author_display_name_2 = "Test Author 2"
        cls.author_github_2 = "github.com/testauthor2"
        author_2 = Author(id=cls.author_id_2, host=cls.author_host_2,
                          display_name=cls.author_display_name_2,
                          github=cls.author_github_2)
        author_2.save()

        # Set up some test post categories
        cls.category_name_1 = "Test Category One"
        cls.category_name_2 = "Test Category Two"
        cls.category_name_3 = "Test Category Three"
        PostCategory(name=cls.category_name_1).save()
        PostCategory(name=cls.category_name_2).save()
        PostCategory(name=cls.category_name_3).save()

        # Set up a test post
        cls.post_id = uuid.uuid4()
        cls.post_title = "Test Post"
        cls.post_source = "SomeTestWebsite.com/posts/"
        cls.post_origin = "SomeOtherTestWebsite.com/posts/"
        cls.post_description = "A small test post."
        cls.post_content_type = "text/plain"
        cls.post_text_content = "This is a test post. It doesn't have much to it."
        post = Post(id=cls.post_id, title=cls.post_title, source=cls.post_source,
                    origin=cls.post_origin, description=cls.post_description,
                    content_type=post_content_type, text_content=post_text_content,
                    author=cls.author_1)
        post.categories.add(cls.category1, cls.category2, cls.category3)
        post.save()

        # Set up test comment
        cls.comment_id = uuid.uuid4()
        cls.comment_comment = "This is a test comment from a different author."
        cls.comment_content_type = "text/plain"
        comment = Comment(id=cls.comment_id, post=cls.post, author=cls.author_2,
                            comment=cls.comment_comment, content_type=cls.comment_content_type)
        comment.save()

    def test_comment_relationship(cls):
        """
        Tests a lengthy reverse-relationship lookup to make sure
        that comments, authors, and posts are related appropriately
        """
        author = Author.objects.filter(comment__post__author__id=cls.author_id_1).all()[0]
        cls.assertEqual(cls.author_display_name_2, author.display_name)

    def test_author_url(cls):
        """
        Tests that the auto-constructed URL is formed as expected for an author.
        It is important that this is consistent since it's key to identifying 
        authors on other servers.
        """
        test_url = "http://{}/author/{}/".format(settings.HOST_NAME, cls.author_id_1)
        cls.assertEqual(test_url, Author.objects.get(pk=cls.author_id_1).url)

    def test_post_url(cls):
        """
        Tests that the auto-constructed URL is formed as expected for a post.
        It is important that this is consistent since it's key to identifying
        posts on other servers.
        """
        test_url = "http://{}/author/{}/posts/{}/".format(settings.HOST_NAME, cls.author_id_1, cls.post_id)
        cls.assertEqual(test_url, Post.objects.get(pk=cls.post_id).url)

    def test_comment_url(cls):
        """
        Tests that the auto-constructed URL is formed as expected for a comment.
        It is important that this is consistent since it's key to identifying
        comments on other servers.
        """
        test_url = "http://{}/author/{}/posts/{}/comments/{}/".format(settings.HOST_NAME, cls.author_id_1, cls.post_id, cls.comment_id)
        cls.assertEqual(test_url, Comment.objects.get(pk=cls.comment_id).url)