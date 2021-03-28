"""
Uses Django's TestCase to run unit tests on our REST API endpoints.
This ensures each test is run inside a transaction to provide isolation.
"""
import uuid, json
from django.test import TestCase, Client
from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from .models import Author, PostCategory, Post, Comment, InboxItem
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
        cls.author_username_1 = "TestAuthor1"
        cls.author_github_1 = "github.com/testauthor1"
        author_1 = Author(id=cls.author_id_1, host=cls.author_host_1,
                          github=cls.author_github_1, username=cls.author_username_1)
        author_1.save()

        cls.author_id_2 = uuid.uuid4()
        cls.author_host_2 = settings.HOST_NAME
        cls.author_username_2 = "TestAuthor2"
        cls.author_github_2 = "github.com/testauthor2"
        author_2 = Author(id=cls.author_id_2, host=cls.author_host_2,
                          github=cls.author_github_2, username=cls.author_username_2)
        author_2.save()

        # Set up a test server user
        cls.server_id = uuid.uuid4()
        cls.server_host = settings.HOST_NAME
        cls.server_username = "server"
        server = Author(id=cls.server_id, host=cls.server_host, username=cls.server_username, is_server=True)

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
        cls.post_content = "This is a test post. It doesn't have much to it."
        post = Post(id=cls.post_id, title=cls.post_title, source=cls.post_source,
                    origin=cls.post_origin, description=cls.post_description,
                    content_type=cls.post_content_type, content=cls.post_content,
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

        # Set up a test inbox item (sharing a post)
        # test post from above is by author_id_1, and we'll put it in author_id_2's inbox
        cls.inbox_item_post_link = "http://127.0.0.1:8000/author/"+str(Post.objects.get(pk=cls.post_id).author.id)+"/posts/"+str(Post.objects.get(pk=cls.post_id).id)+"/"
        inbox_item = InboxItem(author=Author.objects.get(pk=cls.author_id_2), link=cls.inbox_item_post_link)
        inbox_item.save()

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
        client = Client()
        url = reverse("Author", kwargs={"author_id":cls.author_id_2})

        # Modify the author's information via POST
        new_username = "TestAuthor3"
        new_github = "github.com/testauthor3"
        json = {
            "displayName":new_username,
            "github":new_github
        }
        
        # Test unauthenticated request
        response = client.post(url, json, content_type="application/json")
        cls.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Force an incorrect test login and test incorrectly authenticated request
        client.force_login(Author.objects.get(pk=cls.author_id_1))
        response = client.post(url, json, content_type="application/json")
        cls.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Force a test login as the second author and test authenticated request
        client.force_login(Author.objects.get(pk=cls.author_id_2))
        response = client.post(url, json, content_type="application/json")
        cls.assertEqual(response.status_code, status.HTTP_200_OK)

        # Try GET on updated object and see if they match
        response = client.get(url)
        cls.assertEqual(response.status_code, status.HTTP_200_OK)
        cls.assertEqual(response.json(), AuthorToJSON(Author.objects.get(pk=cls.author_id_2)))

        # Test a request on an object that doesn't exist
        url = reverse("Author", kwargs={"author_id":uuid.uuid4()})
        response = client.post(url, json, content_type="application/json")
        cls.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Test a request with an invalid ID
        url = reverse("Author", kwargs={"author_id":"abc"})
        response = client.post(url, json, content_type="application/json")
        cls.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_author_get(cls):
        """
        Test the GET authors/ endpoint
        """
        client = Client()
        url = reverse("AllAuthors")

        # Test unauthenticated 
        response = client.get(url)
        cls.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test bad non-server user
        client.force_login(Author.objects.get(pk=cls.author_id_1))
        response = client.get(url)
        cls.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test good request
        client.force_login(Author.objects.get(pk=cls.server_id))
        response = client.get(url)
        cls.assertEqual(response.status_code, status.HTTP_200_OK)

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
        client = Client()
        url = reverse("Post", kwargs={"author_id":cls.author_id_1, "post_id":cls.post_id})

        new_title = "Test Post 2"
        new_description = "A changed test post"
        new_content_type = "text/markdown"
        new_content = "Some different body text."
        new_visibility = "FRIENDS"
        new_categories = ["Test Category 4", "Test Category 5"]
        new_unlisted = True
        json = {
            "title":new_title,
            "description":new_description,
            "contentType":new_content_type,
            "content":new_content,
            "categories":new_categories,
            "visibility":new_visibility,
            "unlisted":new_unlisted
        }

        # Test unauthenticated request
        response = client.post(url, json, content_type="application/json")
        cls.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Force a bad test login and test incorrectly authenticated request
        client.force_login(Author.objects.get(pk=cls.author_id_2))
        response = client.post(url, json, content_type="application/json")
        cls.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Force a test login and test authenticated request
        client.force_login(Author.objects.get(pk=cls.author_id_1))
        response = client.post(url, json, content_type="application/json")
        cls.assertEqual(response.status_code, status.HTTP_200_OK)

        # Try GET on updated object and see if they match
        response = client.get(url)
        cls.assertEqual(response.status_code, status.HTTP_200_OK)
        cls.assertEqual(response.json(), PostToJSON(Post.objects.get(pk=cls.post_id)))

        # Test a request on an object that doesn't exist (author has no posts)
        url = reverse("Post", kwargs={"author_id":cls.author_id_2, "post_id":cls.post_id})
        response = client.post(url, json, content_type="application/json")
        cls.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Test a request on an object that doesn't exist (bad post ID)
        url = reverse("Post", kwargs={"author_id":cls.author_id_1, "post_id":uuid.uuid4()})
        response = client.post(url, json, content_type="application/json")
        cls.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Test a request with an invalid ID (bad author ID)
        url = reverse("Post", kwargs={"author_id":"abc", "post_id":cls.post_id})
        response = client.post(url, json, content_type="application/json")
        cls.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test a request with an invalid ID (bad post ID)
        url = reverse("Post", kwargs={"author_id":cls.author_id_1, "post_id":"abc"})
        response = client.post(url, json, content_type="application/json")
        cls.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_delete(cls):
        """
        Test the DELETE author/{AUTHOR_ID}/posts/{POST_ID}/ endpoint
        """
        client = Client()
        url = reverse("Post", kwargs={"author_id":cls.author_id_1, "post_id":cls.post_id})

        # Test unauthenticated request
        response = client.delete(url)
        cls.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Force a bad test login and test incorrectly authenticated request
        client.force_login(Author.objects.get(pk=cls.author_id_2))
        response = client.delete(url)
        cls.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Force a good test login and test authenticated request
        client.force_login(Author.objects.get(pk=cls.author_id_1))
        response = client.delete(url)
        cls.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test a request on an object that doesn't exist (author has no posts)
        url = reverse("Post", kwargs={"author_id":cls.author_id_2, "post_id":cls.post_id})
        response = client.delete(url)
        cls.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Test a request on an object that doesn't exist (bad post ID)
        url = reverse("Post", kwargs={"author_id":cls.author_id_1, "post_id":uuid.uuid4()})
        response = client.delete(url)
        cls.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Test a request with an invalid ID (bad author ID)
        url = reverse("Post", kwargs={"author_id":"abc", "post_id":cls.post_id})
        response = client.delete(url)
        cls.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test a request with an invalid ID (bad post ID)
        url = reverse("Post", kwargs={"author_id":cls.author_id_1, "post_id":"abc"})
        response = client.delete(url)
        cls.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_put(cls):
        """
        Test the PUT author/{AUTHOR_ID}/posts/{POST_ID}/ endpoint
        """
        client = Client()
        new_post_id = uuid.uuid4()
        url = reverse("Post", kwargs={"author_id":cls.author_id_2, "post_id":new_post_id})

        new_title = "Test Post 2"
        new_source = "SomeTestWebsite.com/posts/"
        new_origin = "SomeOtherTestWebsite.com/posts/"
        new_description = "A changed test post"
        new_content_type = "text/markdown"
        new_content = "Some different body text."
        new_visibility = "FRIENDS"
        new_unlisted = True
        json = {
            "title":new_title,
            "source":new_source,
            "origin":new_origin,
            "description":new_description,
            "contentType":new_content_type,
            "content":new_content,
            "visibility":new_visibility,
            "unlisted":new_unlisted
        }

        # Test unauthenticated request
        response = client.put(url, json, content_type="application/json")
        cls.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test incorrectly authenticated request
        client.force_login(Author.objects.get(pk=cls.author_id_1))
        response = client.put(url, json, content_type="application/json")
        cls.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test correctly authenticated request
        client.force_login(Author.objects.get(pk=cls.author_id_2))
        response = client.put(url, json, content_type="application/json")
        cls.assertEqual(response.status_code, status.HTTP_200_OK)

        # Try GET on updated object and see if they match
        response = client.get(url)
        cls.assertEqual(response.status_code, status.HTTP_200_OK)
        cls.assertEqual(response.json(), PostToJSON(Post.objects.get(pk=new_post_id)))

        # Test a request on an object that doesn't exist (author doesn't exist)
        url = reverse("Post", kwargs={"author_id":new_post_id, "post_id":new_post_id})
        response = client.put(url, json, content_type="application/json")
        cls.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Test a request with an invalid ID (bad author ID)
        url = reverse("Post", kwargs={"author_id":"abc", "post_id":new_post_id})
        response = client.put(url, json, content_type="application/json")
        cls.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test a request with an invalid ID (bad post ID)
        url = reverse("Post", kwargs={"author_id":cls.author_id_2, "post_id":"abc"})
        response = client.put(url, json, content_type="application/json")
        cls.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_all_post_get(cls):
        """
        Test the GET posts/ endpoint
        """
        client = Client()
        url = reverse("AllPosts")

        # Test unauthenticated 
        response = client.get(url)
        cls.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test bad non-server user
        client.force_login(Author.objects.get(pk=cls.author_id_1))
        response = client.get(url)
        cls.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test good request
        client.force_login(Author.objects.get(pk=cls.server_id))
        response = client.get(url)
        cls.assertEqual(response.status_code, status.HTTP_200_OK)

    # TODO: Fill out this test
    def test_all_author_post_get(cls):
        """
        Test the GET author/{AUTHOR_ID}/posts/ endpoint
        """
        # Test a good request
        client = Client()
        url = reverse("AuthorPosts", kwargs={"author_id":cls.author_id_1})
        response = client.get(url)
        cls.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test a request with an invalid ID (bad author ID)
        url = reverse("AuthorPosts", kwargs={"author_id":"abc"})
        response = client.get(url)
        cls.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # TODO: Fill out this test
    def test_all_author_post_post(cls):
        """
        Test the POST author/{AUTHOR_ID}/posts/ endpoint
        """
        client = Client()
        url = reverse("AuthorPosts", kwargs={"author_id":cls.author_id_2})

        new_title = "Test Post 2"
        new_source = "SomeTestWebsite.com/posts/"
        new_origin = "SomeOtherTestWebsite.com/posts/"
        new_description = "A changed test post"
        new_content_type = "text/markdown"
        new_content = "Some different body text."
        new_visibility = "FRIENDS"
        new_unlisted = True
        json = {
            "title":new_title,
            "source":new_source,
            "origin":new_origin,
            "description":new_description,
            "contentType":new_content_type,
            "content":new_content,
            "visibility":new_visibility,
            "unlisted":new_unlisted
        }

        # Test unauthenticated request
        response = client.post(url, json, content_type="application/json")
        cls.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test request with bad authentication
        client.force_login(Author.objects.get(pk=cls.author_id_1))
        response = client.post(url, json, content_type="application/json")
        cls.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test request with good authentication
        client.force_login(Author.objects.get(pk=cls.author_id_2))
        response = client.post(url, json, content_type="application/json")
        cls.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test a request with an invalid ID (bad author ID)
        url = reverse("AuthorPosts", kwargs={"author_id":"abc"})
        response = client.post(url, json, content_type="application/json")
        cls.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # TODO: Fill out this test
    def test_comment_get(cls):
        """
        Test the GET author/{AUTHOR_ID}/posts/{POST_ID}/comments/ endpoint
        """
        # Test a good request
        client = Client()
        url = reverse("PostComments", kwargs={"author_id":cls.author_id_1, "post_id":cls.post_id})
        response = client.get(url)
        cls.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test a request on an object that doesn't exist (author has no posts)
        url = reverse("PostComments", kwargs={"author_id":cls.author_id_2, "post_id":cls.post_id})
        response = client.get(url)
        cls.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Test a request on an object that doesn't exist (bad post ID)
        url = reverse("PostComments", kwargs={"author_id":cls.author_id_1, "post_id":uuid.uuid4()})
        response = client.get(url)
        cls.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Test a request with an invalid ID (bad author ID)
        url = reverse("PostComments", kwargs={"author_id":"abc", "post_id":cls.post_id})
        response = client.get(url)
        cls.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test a request with an invalid ID (bad post ID)
        url = reverse("PostComments", kwargs={"author_id":cls.author_id_1, "post_id":"abc"})
        response = client.get(url)
        cls.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # TODO: Fill out this test
    def test_comment_post(cls):
        """
        Test the POST author/{AUTHOR_ID}/posts/{POST_ID}/comments/ endpoint
        """
        client = Client()
        url = reverse("PostComments", kwargs={"author_id":cls.author_id_1, "post_id":cls.post_id})

        new_content_type = "text/markdown"
        new_comment = "This post is the best."
        json = {
            "contentType":new_content_type,
            "comment":new_comment
        }

        # Test unauthenticated request
        response = client.post(url, json, content_type="application/json")
        cls.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test authenticated request
        client.force_login(Author.objects.get(pk=cls.author_id_2))
        response = client.post(url, json, content_type="application/json")
        cls.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test a request on an object that doesn't exist (author has no posts)
        url = reverse("PostComments", kwargs={"author_id":cls.author_id_2, "post_id":cls.post_id})
        response = client.post(url, json, content_type="application/json")
        cls.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Test a request on an object that doesn't exist (bad post ID)
        url = reverse("PostComments", kwargs={"author_id":cls.author_id_1, "post_id":uuid.uuid4()})
        response = client.post(url, json, content_type="application/json")
        cls.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Test a request with an invalid ID (bad author ID)
        url = reverse("PostComments", kwargs={"author_id":"abc", "post_id":cls.post_id})
        response = client.post(url, json, content_type="application/json")
        cls.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test a request with an invalid ID (bad post ID)
        url = reverse("PostComments", kwargs={"author_id":cls.author_id_1, "post_id":"abc"})
        response = client.post(url, json, content_type="application/json")
        cls.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_inbox_get(cls):
        """Test the GET author/{AUTHOR_ID}/inbox/ endpoint"""
        AUTHOR_ID = cls.author_id_2
        client = Client()
        url = reverse("inbox", kwargs={"author_id":AUTHOR_ID})
        # Get inbox without auth
        response = client.get(url)
        cls.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # Get inbox WITH auth (Y. Alaqra https://stackoverflow.com/q/55033950)
        factory = APIRequestFactory()
        view = views.InboxEndpoint.as_view()
        user = Author.objects.get(pk=AUTHOR_ID)
        request = factory.get(url)
        force_authenticate(request, user=user)
        # Problem: InboxItemToJSON won't be able to get the right json because
        # the app isn't actually running. (Returns the placeholder json)
        response = view(request, author_id=str(AUTHOR_ID))
        cls.assertEqual(response.status_code, status.HTTP_200_OK)
        cls.assertEqual(response.get("Content-Type"), "application/json")
        response_content = json.loads(response.content.decode('utf-8'))
        cls.assertNotEqual(len(response_content["items"]), 0)
    
    
    def test_inbox_post(cls):
        """Test the POST author/{AUTHOR_ID}/inbox/ endpoint"""
        AUTHOR_ID = cls.author_id_2
        client = Client()
        url = reverse("inbox", kwargs={"author_id":AUTHOR_ID})
        to_post = { "link":cls.inbox_item_post_link }
        # POST to an author's inbox without auth
        response = client.post(url, to_post, content_type="application/json")
        cls.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # POST to an author's inbox WITH auth
        factory = APIRequestFactory()
        view = views.InboxEndpoint.as_view()
        user = Author.objects.get(pk=AUTHOR_ID)
        request = factory.post(url, to_post)
        force_authenticate(request, user=user)
        response = view(request, author_id=str(AUTHOR_ID))
        cls.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Now GET to make sure
        request = factory.get(url)
        force_authenticate(request, user=user)
        response = view(request, author_id=str(AUTHOR_ID))
        cls.assertEqual(response.status_code, status.HTTP_200_OK)
        cls.assertEqual(response.get("Content-Type"), "application/json")
        response_content = json.loads(response.content.decode('utf-8'))
        # setUp already saved one InboxItem, so now we should have two
        cls.assertEqual(len(response_content["items"]), 2)


    def test_inbox_delete(cls):
        """Test the DELETE author/{AUTHOR_ID}/inbox/ endpoint"""
        AUTHOR_ID = cls.author_id_2
        client = Client()
        url = reverse("inbox", kwargs={"author_id":AUTHOR_ID})
        # DELETE (clear the inbox) without auth
        response = client.delete(url)
        cls.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # DELETE (clear the inbox) with auth
        factory = APIRequestFactory()
        view = views.InboxEndpoint.as_view()
        user = Author.objects.get(pk=AUTHOR_ID)
        request = factory.delete(url)
        force_authenticate(request, user=user)
        response = view(request, author_id=str(AUTHOR_ID))
        cls.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Now GET to make sure
        request = factory.get(url)
        force_authenticate(request, user=user)
        response = view(request, author_id=str(AUTHOR_ID))
        cls.assertEqual(response.status_code, status.HTTP_200_OK)
        cls.assertEqual(response.get("Content-Type"), "application/json")
        response_content = json.loads(response.content.decode('utf-8'))
        cls.assertEqual(len(response_content["items"]), 0) # is it empty?