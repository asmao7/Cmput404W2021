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
   # Models information about a user 
   id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
   host = models.CharField(max_length=100, default=settings.HOST_NAME, editable=False)
   display_name = models.CharField(max_length=100)
   url = models.CharField(max_length=200, editable=False)
   github = models.CharField(max_length=200)

   # Overwrite the default save function so that we can generate our URL
   def save(self, *args, **kwargs):
       if not self.url:
           self.url = "http://{}/author/{}/".format(self.host, self.id)
       super(Author, self).save(*args, **kwargs)


class PostCategory(models.Model):
    # Models a category that a post can belong to
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = "Post Category"
        verbose_name_plural = "Post Categories"


class Post(models.Model):
    # Abstract model used as the base for Posts

    VISIBILITY_CHOICES = [
        ("PUBLIC", "Public"),
        ("FRIENDS", "Friends"),
    ]

    CONTENT_TYPE_CHOICES = [
        ("text/plain", "Plain Text"),
        ("text/markdown", "Markdown"),
        ("application/base64", "Base64 Encoding"),
        ("image/png;base64", "PNG"),
        ("image/jpeg;base64", "JPEG"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    url = models.CharField(max_length=200)
    source = models.CharField(max_length=200)
    origin = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES, default="text/plain")
    text_content = models.TextField()
    image_content = models.ImageField(upload_to="post_images")
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    categories = models.ManyToManyField(PostCategory, blank=True)
    published = models.DateTimeField(auto_now_add=True)
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default="PUBLIC")
    unlisted = models.BooleanField(default=False)


class Comment(models.Model):
    # Models a comment on a post

    CONTENT_TYPE_CHOICES = [
        ("text/plain", "Plain Text"),
        ("text/markdown", "Markdown"),
    ]

    id = models.UUIDField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    comment = models.TextField()
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES, default="text/plain")
    published = models.DateTimeField(auto_now_add=True)
    url = models.CharField(max_length=200)