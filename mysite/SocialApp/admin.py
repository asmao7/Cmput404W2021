"""
Contains Django admin related configurations
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import Post, Author, PostCategory, Comment, LikedPost

class DefaultAdmin(admin.ModelAdmin):
    """
    Default model representation in Django admin
    """
    pass


class AuthorCreationForm(UserCreationForm):
    """
    Custom form for creating new users
    """
    class Meta:
        model = Author
        fields = UserCreationForm.Meta.fields + ("display_name", "github",)


#TODO: Find a way to display read-only fields
class AuthorChangeForm(UserChangeForm):
    """
    Custom form for editing users
    """
    class Meta:
        model = Author
        fields = ("username", "password", "first_name", "last_name", "display_name", "email", "github", "is_active", "is_staff", "is_superuser", "groups", "user_permissions",)


class AuthorAdmin(UserAdmin):
    """
    Author model representation ni Django admin
    """
    model = Author
    form = AuthorChangeForm

# Set some admin site variables
admin.site.site_header = "Social Distribution Project Admin"
admin.site.site_title = "Social Distribution Project Admin"
admin.site.index_title = "Welcome to the administration portal"

# Register our models with the admin site
admin.site.register(Author, AuthorAdmin)
admin.site.register(Post, DefaultAdmin)
admin.site.register(PostCategory, DefaultAdmin)
admin.site.register(Comment, DefaultAdmin)
admin.site.register(LikedPost, DefaultAdmin)


