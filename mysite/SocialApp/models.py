"""
Contains the models necessary for our application
"""
import uuid
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext_lazy
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.core.exceptions import ValidationError

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
    # URL that points to the REST api endpoint for this author - also used as the "id" in the protocol
    url = models.CharField(max_length=200, editable=False)
    # URL to the user's github. Editable by the user.
    github = models.CharField(max_length=200, blank=True)
    # Whether or not this account is allowed to log-in (default driven by settings.py)
    is_active = models.BooleanField(default=settings.NEW_ACCOUNTS_AUTO_APPROVED)
    #followers stores the number of users following the current user linking them through the intermediate table Followers
    followers = models.ManyToManyField('self', through='Followers',symmetrical=False,related_name='followed_by')
    # Whether or not this account should be treated as a friendly server and get elevated permissions
    is_server = models.BooleanField(default=False)

    def __str__(self):
        return self.username

    # Overwrite the default save function so that we can generate our URL
    def save(self, *args, **kwargs):
        if not self.url:
            self.url = "{}://{}/author/{}/".format(settings.SCHEME, settings.HOST_NAME, self.id)
        super(Author, self).save(*args, **kwargs)


class PostCategory(models.Model):
    """
    Models a category that a post can belong to
    """
    # Unique names prevents duplicate entries from appearing in the database
    # prefer to re-use existing categories where possible
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

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
    # Short description of the post
    description = models.CharField(max_length=200)
    # The content type of the post. Must be one of a few specific types.
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES, default="text/plain")
    # The content associated with this post. If the post is an image, should be base64 encoded text.
    content = models.TextField(blank=True, default="")
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

    def __str__(self):
        return self.title

    # Overwrite the default save function so that we can generate our URL
    def save(self, *args, **kwargs):
        if not self.url:
            self.url = "{}://{}/author/{}/posts/{}/".format(settings.SCHEME, settings.HOST_NAME, self.author.id, self.id)
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
    author_url = models.CharField(max_length=200, blank=True, default="")
    # Backup author JSON (will go stale)
    author_json = models.TextField(default="")
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
            self.url = "{}://{}/author/{}/posts/{}/comments/{}/".format(settings.SCHEME, settings.HOST_NAME, self.post.author.id, self.post.id, self.id)
        super(Comment, self).save(*args, **kwargs)


class ObjectLike(models.Model):
    """
    Models a liked object
    """
    # URL of the author who liked the object
    author_url = models.CharField(max_length=200)
    # JSON of the author who liked the object (will go stale)
    author_json = models.TextField(default="")
    # URL of the object being liked
    object_url = models.CharField(max_length=200)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["author_url", "object_url"], name="unique_like")
        ]
        verbose_name = "Liked Object"
        verbose_name_plural = "Liked Objects"


class Followers(models.Model):
    """ get a specific user's followers """
    #the author sending the follow request 
    #reverse relationship author.following get all the people the author is  following
    author_from = models.ForeignKey(Author, related_name='following', on_delete=models.CASCADE) 
    #the author that is being followed
    #reverse relationship author.followee get all their followers (all the people currently following the user) 
    author_to = models.ForeignKey(Author, related_name='followee', on_delete=models.CASCADE, default=None) 

    # prohibit following same person twice
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['author_from','author_to'],  name="unique_follow")
        ]
        # Helpful for Django Admin
        verbose_name = "Followers"
        verbose_name_plural = "Followers"


class ForeignServer(models.Model):
    """
    Models a fetch-content relationship with a foreign server
    """
    # A name by which to more easily identify the server
    name = models.CharField(max_length=100)
    # Whether or not to try and connect to this server
    is_active = models.BooleanField(default=True)
    # Host name - used to check URLs for matches
    host_name = models.CharField(max_length=100, blank=True)
    # The url to get all of the authors on the server (leave blank if unsupported)
    authors_url = models.CharField(max_length=200, blank=True)
    # The key to look at for the JSON list of authors
    authors_json_key = models.CharField(max_length=25, blank=True)
    # The url to get all of the posts on the server (leave blank if unsupported)
    posts_url = models.CharField(max_length=200, blank=True)
    # The key to look at for the JSON list of posts
    posts_json_key = models.CharField(max_length=25, blank=True)
    # The username credentials for connecting to the server with basic auth (leave blank if unsupported)
    username = models.CharField(max_length=100, blank=True)
    # The password credentials for connecting to the server with basic auth (leave blank if unsupported)
    password = models.CharField(max_length=25, blank=True)

    class Meta:
        verbose_name = "Foreign Server"
        verbose_name_plural = "Foreign Servers"


#prohibit self following 
@receiver(pre_save, sender=Followers)
def check_self_following(sender, instance, **kwargs):
    if instance.author_from == instance.author_to:
        raise ValidationError('ERROR!!, you cannot follow yourself ')

class InboxItem(models.Model):
    """ 
    An item in an Author's inbox. 
    `author` is the id of the user that you wish to share this item with.
    `json_str` contains a JSON string. That means an InboxItem can contain
    a post, like, or follow.
    `link` is a complete permalink to whatever you're sharing (optional)
    """
    author = models.ForeignKey(Author, on_delete=models.CASCADE) # the recipient
    link = models.TextField(default="")
    json_str = models.TextField(default="")

class RemoteFollow(models.Model):
    """ keep track of the remote authors that an author is following """
    #the author sending the follow request 
    local_author_from = models.ForeignKey(Author, related_name='remote_following', on_delete=models.CASCADE) 
    #the author that is being followed
    remote_author_to = models.CharField(max_length=200, editable=False)

    # make relationship unique
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['local_author_from','remote_author_to'],  name="remote_follow")
        ]

class RemoteFollowers(models.Model):
    """ keep track of the remote authors that are following the current """
    #the author sending the follow request 
    remote_author_from = models.CharField(max_length=200, editable=False) 
    #the author that is being followed
    local_author_to = models.ForeignKey(Author, related_name='remote_followers', on_delete=models.CASCADE) 

    # make relationship unique
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['remote_author_from','local_author_to'],  name="remote_followers")
        ]
        verbose_name = "Remote Follower"
        verbose_name_plural = "Remote Followers"