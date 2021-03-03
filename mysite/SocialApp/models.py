"""
Contains the models necessary for our application
"""
import uuid
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.utils.translation import gettext_lazy

#NOTE: django gives each model an auto generated id field:  id = models.AutoField(primary_key=True, **options)
#NOTE: Django admin panels use __str__ to generate labels, so explicitly definiting them is important
#NOTE: Django model class can have a "Meta" subclass to fill out additional metadata. More info here: https://docs.djangoproject.com/en/3.1/ref/models/options/
#NOTE: As per the docs, model fields should be lower case, separated by underscores

class Author(AbstractUser):
    """
    Models information about a user
    """
    # Used to uniquely identify an author on our server. Will be part of related URLs
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Automatically derived from the HOST_NAME field in settings.py
    host = models.CharField(max_length=100, default=settings.HOST_NAME, editable=False)
    # Self-identification by the author. Not used for authentication.
    display_name = models.CharField(max_length=100)
    # URL that points to the REST api endpoint for this author - also used as the "id" in the protocol
    url = models.CharField(max_length=200, editable=False)
    # URL to the user's github. Editable by the user.
    github = models.CharField(max_length=200)

    # Overwrite the default save function so that we can generate our URL
    def save(self, *args, **kwargs):
        if not self.url:
            self.url = "http://{}/author/{}/".format(settings.HOST_NAME, self.id)
        super(Author, self).save(*args, **kwargs)


class PostCategory(models.Model):
    """
    Models a category that a post can belong to
    """
    # Unique names prevents duplicate entries from appearing in the database
    # prefer to re-use existing categories where possible
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        # Helpful for Django Admin
        verbose_name = "Post Category"
        verbose_name_plural = "Post Categories"


class Post(models.Model):
    """
    Models a post created by an author
    """
    # Used to define valid visibility strings
    VISIBILITY_CHOICES = [
        ("PUBLIC", "Public"),
        ("FRIENDS", "Friends"),
    ]

    # Used to define valid content-type strings for posts (text or image based)
    CONTENT_TYPE_CHOICES = [
        ("text/plain", "Plain Text"),
        ("text/markdown", "Markdown"),
        ("application/base64", "Base64 Encoding"),
        ("image/png;base64", "PNG"),
        ("image/jpeg;base64", "JPEG"),
    ]

    # Uniquely identifies a post on our server. Will be part of the related URLs
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # The title of the post. Set by the author.
    title = models.CharField(max_length=200)
    # URL that points to the REST api endpoint for this post - also used as the "id" in the protocol
    url = models.CharField(max_length=200, editable=False)
    # The server we got this from. We can change this programatically
    source = models.CharField(max_length=200)
    # The server this originated on. Immutable.
    origin = models.CharField(max_length=200, editable=False)
    # Short description of the post
    description = models.CharField(max_length=200)
    # The content type of the post. Must be one of a few specific types.
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES, default="text/plain")
    # The text-based content associated with this post. If the post is an image, should point to that image.
    text_content = models.TextField(blank=True, default="")
    # The image-based content associated with this post. If the post is a text post, should be null
    image_content = models.ImageField(upload_to="post_images", blank=True, null=True)
    # The author of this post
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    # The categories this post has been tagged with
    categories = models.ManyToManyField(PostCategory, blank=True)
    # The time that the post was originally published
    published = models.DateTimeField(auto_now_add=True)
    # Privacy settings for the post
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default="PUBLIC")
    # Whether or not this post should show up in feeds, or is only accessible via URL
    unlisted = models.BooleanField(default=False)

    # Overwrite the default save function so that we can generate our URL
    def save(self, *args, **kwargs):
        if not self.url:
            self.url = "http://{}/author/{}/posts/{}/".format(settings.HOST_NAME, self.author.id, self.id)
        super(Post, self).save(*args, **kwargs)


class Comment(models.Model):
    """
    Models a comment on a post
    """
    # Used to define valid content-type strings for comments (text based)
    CONTENT_TYPE_CHOICES = [
        ("text/plain", "Plain Text"),
        ("text/markdown", "Markdown"),
    ]

    # Uniquely identifies a comment on our server. Will be part of the related URLs
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # The post this comment is attached to
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    # The author of this comment (not to be confused with the author of the post)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    # The text content content of the comment
    comment = models.TextField()
    # The content type of the comment. Must be one of a few specific types.
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES, default="text/plain")
    # The time that the comment was originally published
    published = models.DateTimeField(auto_now_add=True)
    # URL that points to the REST api endpoint for this comment - also used as the "id" in the protocol
    url = models.CharField(max_length=200, editable=False)

    # Overwrite the default save function so that we can generate our URL
    def save(self, *args, **kwargs):
        if not self.url:
            self.url = "http://{}/author/{}/posts/{}/comments/{}/".format(settings.HOST_NAME, self.post.author.id, self.post.id, self.id)
        super(Comment, self).save(*args, **kwargs)