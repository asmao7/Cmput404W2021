import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy

#NOTE: django gives each model an auto generated id field:  id = models.AutoField(primary_key=True, **options)
#NOTE: Django admin panels use __str__ to generate labels, so explicitly definiting them is important
#NOTE: Django model class can have a "Meta" subclass to fill out additional metadata. More info here: https://docs.djangoproject.com/en/3.1/ref/models/options/
#NOTE: As per the docs, model fields should be lower case, separated by underscores

# TODO: Some of the URL fields are stand-ins for IDs - may need to change that
class Author(models.Model):
   # Models information about a user 
   base_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
   user_object = models.OneToOneField(User, on_delete=models.CASCADE)
   host = models.CharField(max_length=100)
   display_name = models.CharField(max_length=100)
   url = models.CharField(max_length=200)
   github = models.CharField(max_length=200)


class PostCategory(models.Model):
    # Models a category that a post can belong to
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Post Category"
        verbose_name_plural = "Post Categories"


class Post(models.Model):
    # Abstract model used as the base for Posts

    class Visibility(models.IntegerChoices):
        # Works kind of like an enum
        PUBLIC = 0, gettext_lazy("PUBLIC")
        FRIENDS = 1, gettext_lazy("FRIENDS")

    title = models.CharField(max_length=200)
    url = models.CharField(max_length=200)
    source = models.CharField(max_length=200)
    origin = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    content_type = models.CharField(max_length=50)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    categories = models.ManyToManyField(PostCategory)
    published = models.DateTimeField(auto_now_add=True)
    visibility = models.IntegerField(choices=Visibility.choices, default=Visibility.PUBLIC)
    unlisted = models.BooleanField()

    class Meta:
        abstract = True


# TODO: Have to handle plain-text and markdown
class TextPost(Post):
    # Models a post with text content
    content = models.TextField()

    class Meta:
        verbose_name = "Text Post"
        verbose_name_plural = "Text Posts"


# TODO: Have to handle different types of images
class ImagePost(Post):
    # Models a post with image content
    content = models.ImageField(upload_to="post_images")

    class Meta:
        verbose_name = "Image Post"
        verbose_name_plural = "Image Posts"


class Comment(models.Model):
    # Models a comment on a post
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    comment = models.TextField()
    content_type = models.CharField(max_length=50)
    published = models.DateTimeField(auto_now_add=True)
    url = models.CharField(max_length=200)