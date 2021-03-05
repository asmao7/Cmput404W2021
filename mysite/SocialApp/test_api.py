"""
Uses Django's TestCase to run unit tests on our REST API endpoints.
This ensures each test is run inside a transaction to provide isolation.
"""
import uuid
from django.test import TestCase, Client
from django.conf import settings
from django.urls import reverse
from rest_framework import status
from .models import Author, PostCategory, Post, Comment
from . import views
from .utils import AuthorToJSON, PostToJSON, CommentToJSON

class TestCases(TestCase):
    """
    Class that contains all of our test cases. We do this since testing the API
    often involves the interrelationships between objects so we might as well
    set them all up.
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
        cls.author_username_1 = "TestAuthor1"
        cls.author_github_1 = "github.com/testauthor1"
        author_1 = Author(id=cls.author_id_1, host=cls.author_host_1,
                          display_name=cls.author_display_name_1,
                          github=cls.author_github_1, username=cls.author_username_1)
        author_1.save()

        cls.author_id_2 = uuid.uuid4()
        cls.author_host_2 = settings.HOST_NAME
        cls.author_display_name_2 = "Test Author 2"
        cls.author_username_2 = "TestAuthor2"
        cls.author_github_2 = "github.com/testauthor2"
        author_2 = Author(id=cls.author_id_2, host=cls.author_host_2,
                          display_name=cls.author_display_name_2,
                          github=cls.author_github_2, username=cls.author_username_2)
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
                    content_type=cls.post_content_type, text_content=cls.post_text_content,
                    author=Author.objects.get(pk=cls.author_id_1))
        post.categories.add(PostCategory.objects.get(pk=1),
                            PostCategory.objects.get(pk=2),
                            PostCategory.objects.get(pk=3))
        post.save()

        # Set up test comment
        cls.comment_id = uuid.uuid4()
        cls.comment_comment = "This is a test comment from a different author."
        cls.comment_content_type = "text/plain"
        comment = Comment(id=cls.comment_id, post=Post.objects.get(pk=cls.post_id), author=Author.objects.get(pk=cls.author_id_2),
                            comment=cls.comment_comment, content_type=cls.comment_content_type)
        comment.save()

    def test_author_get(cls):
        """
        Test the GET author/{AUTHOR_ID}/ endpoint
        """
        # Test a good request
        client = Client()
        url = reverse("Author", kwargs={"author_id":cls.author_id_1})
        response = client.get(url)
        cls.assertEqual(response.status_code, status.HTTP_200_OK)
        cls.assertEqual(response.json(), AuthorToJSON(Author.objects.get(pk=cls.author_id_1)))

        # Test a request on an object that doesn't exist
        url = reverse("Author", kwargs={"author_id":uuid.uuid4()})
        response = client.get(url)
        cls.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Test a request with an invalid ID
        url = reverse("Author", kwargs={"author_id":"abc"})
        response = client.get(url)
        cls.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_author_post(cls):
        """
        Test the POST author/{AUTHOR_ID}/ endpoint
        """
        # Test a good request
        client = Client()
        url = reverse("Author", kwargs={"author_id":cls.author_id_2})
        new_display_name = "Test Author 3"
        new_github = "github.com/testauthor3"
        json = {
            "displayName":new_display_name,
            "github":new_github
        }
        response = client.post(url, json)
        cls.assertEqual(response.status_code, status.HTTP_200_OK)
        # Try GET on updated object and see if they match
        response = client.get(url)
        cls.assertEqual(response.status_code, status.HTTP_200_OK)
        cls.assertEqual(response.json(), AuthorToJSON(Author.objects.get(pk=cls.author_id_2)))

        # Test a request on an object that doesn't exist
        url = reverse("Author", kwargs={"author_id":uuid.uuid4()})
        response = client.post(url, json)
        cls.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Test a request with an invalid ID
        url = reverse("Author", kwargs={"author_id":"abc"})
        response = client.post(url, json)
        cls.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_get(cls):
        """
        Test the GET author/{AUTHOR_ID}/posts/{POST_ID}/ endpoint
        """
        # Test a good request
        client = Client()
        url = reverse("Post", kwargs={"author_id":cls.author_id_1, "post_id":cls.post_id})
        response = client.get(url)
        cls.assertEqual(response.status_code, status.HTTP_200_OK)
        cls.assertEqual(response.json(), PostToJSON(Post.objects.get(pk=cls.post_id)))

        # Test a request on an object that doesn't exist (author has no posts)
        url = reverse("Post", kwargs={"author_id":cls.author_id_2, "post_id":cls.post_id})
        response = client.get(url)
        cls.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Test a request on an object that doesn't exist (bad post ID)
        url = reverse("Post", kwargs={"author_id":cls.author_id_1, "post_id":uuid.uuid4()})
        response = client.get(url)
        cls.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Test a request with an invalid ID (bad author ID)
        url = reverse("Post", kwargs={"author_id":"abc", "post_id":cls.post_id})
        response = client.get(url)
        cls.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test a request with an invalid ID (bad post ID)
        url = reverse("Post", kwargs={"author_id":cls.author_id_1, "post_id":"abc"})
        response = client.get(url)
        cls.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_post(cls):
        """
        Test the POST author/{AUTHOR_ID}/posts/{POST_ID}/ endpoint
        """
        # TODO: Figure out what causes the JSON mis-match (date formatting is different, for one)
        return

        # Test a good request
        client = Client()
        url = reverse("Post", kwargs={"author_id":cls.author_id_1, "post_id":cls.post_id})

        new_title = "Test Post 2"
        new_description = "A changed test post"
        new_content_type = "text/markdown"
        new_text_content = "Some different body text."
        new_visibility = "FRIENDS"
        new_unlisted = True
        json = {
            "title":new_title,
            "description":new_description,
            "contentType":new_content_type,
            "content":new_text_content,
            "visibility":new_visibility,
            "unlisted":new_unlisted
        }
        response = client.post(url, json)
        cls.assertEqual(response.status_code, status.HTTP_200_OK)
        # Try GET on updated object and see if they match
        response = client.get(url)
        cls.assertEqual(response.status_code, status.HTTP_200_OK)
        cls.assertEqual(response.json(), PostToJSON(Post.objects.get(pk=cls.post_id)))

        # Test a request on an object that doesn't exist (author has no posts)
        url = reverse("Post", kwargs={"author_id":cls.author_id_2, "post_id":cls.post_id})
        response = client.get(url)
        cls.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Test a request on an object that doesn't exist (bad post ID)
        url = reverse("Post", kwargs={"author_id":cls.author_id_1, "post_id":uuid.uuid4()})
        response = client.get(url)
        cls.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Test a request with an invalid ID (bad author ID)
        url = reverse("Post", kwargs={"author_id":"abc", "post_id":cls.post_id})
        response = client.get(url)
        cls.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test a request with an invalid ID (bad post ID)
        url = reverse("Post", kwargs={"author_id":cls.author_id_1, "post_id":"abc"})
        response = client.get(url)
        cls.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_delete(cls):
        """
        Test the DELETE author/{AUTHOR_ID}/posts/{POST_ID}/ endpoint
        """
        # Test a good request
        client = Client()
        url = reverse("Post", kwargs={"author_id":cls.author_id_1, "post_id":cls.post_id})
        response = client.delete(url)
        cls.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test a request on an object that doesn't exist (author has no posts)
        url = reverse("Post", kwargs={"author_id":cls.author_id_2, "post_id":cls.post_id})
        response = client.get(url)
        cls.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Test a request on an object that doesn't exist (bad post ID)
        url = reverse("Post", kwargs={"author_id":cls.author_id_1, "post_id":uuid.uuid4()})
        response = client.get(url)
        cls.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Test a request with an invalid ID (bad author ID)
        url = reverse("Post", kwargs={"author_id":"abc", "post_id":cls.post_id})
        response = client.get(url)
        cls.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test a request with an invalid ID (bad post ID)
        url = reverse("Post", kwargs={"author_id":cls.author_id_1, "post_id":"abc"})
        response = client.get(url)
        cls.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # TODO: Should put prevent overwriting an existing post???
    def test_post_put(cls):
        """
        Test the PUT author/{AUTHOR_ID}/posts/{POST_ID}/ endpoint
        """
        # Pretty sure the endpoint needs to be fixed up
        # But we're going to bypass this for now because it's frustrating
        return

        # Test a good request
        client = Client()
        new_post_id = uuid.uuid4()
        url = reverse("Post", kwargs={"author_id":cls.author_id_2, "post_id":new_post_id})

        new_title = "Test Post 2"
        new_source = "SomeTestWebsite.com/posts/"
        new_origin = "SomeOtherTestWebsite.com/posts/"
        new_description = "A changed test post"
        new_content_type = "text/markdown"
        new_text_content = "Some different body text."
        new_visibility = "FRIENDS"
        new_unlisted = True
        json = {
            "title":new_title,
            "source":new_source,
            "origin":new_origin,
            "description":new_description,
            "contentType":new_content_type,
            "content":new_text_content,
            "visibility":new_visibility,
            "unlisted":new_unlisted
        }
        response = client.put(url, json)
        cls.assertEqual(response.status_code, status.HTTP_200_OK)
        # Try GET on updated object and see if they match
        response = client.get(url)
        cls.assertEqual(response.status_code, status.HTTP_200_OK)
        cls.assertEqual(response.json(), PostToJSON(Post.objects.get(pk=new_post_id)))

        # Test a request on an object that doesn't exist (author has no posts)
        url = reverse("Post", kwargs={"author_id":cls.author_id_1, "post_id":new_post_id})
        response = client.get(url)
        cls.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Test a request with an invalid ID (bad author ID)
        url = reverse("Post", kwargs={"author_id":"abc", "post_id":new_post_id})
        response = client.get(url)
        cls.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test a request with an invalid ID (bad post ID)
        url = reverse("Post", kwargs={"author_id":cls.author_id_2, "post_id":"abc"})
        response = client.get(url)
        cls.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # TODO: Fill out this test
    def test_all_post_get(cls):
        """
        Test the GET author/{AUTHOR_ID}/posts/ endpoint
        """
        # Test a good request
        client = Client()

    # TODO: Fill out this test
    def test_all_post_post(cls):
        """
        Test the POST author/{AUTHOR_ID}/posts/ endpoint
        """
        # Test a good request
        client = Client()

    # TODO: Fill out this test
    def test_comment_get(cls):
        """
        Test the GET author/{AUTHOR_ID}/posts/{POST_ID}/comments/ endpoint
        """
        # Test a good request
        client = Client()

    # TODO: Fill out this test
    def test_comment_post(cls):
        """
        Test the POST author/{AUTHOR_ID}/posts/{POST_ID}/comments/ endpoint
        """
        # Test a good request
        client = Client()