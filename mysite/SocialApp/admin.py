"""
Contains Django admin related configurations
"""
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import Post, Author, PostCategory, Comment, LikedPost, Followers

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
        fields = UserCreationForm.Meta.fields + ("github",)
        help_texts = {
            "is_active": "Whether or not a user has permission to log-in.",
            "is_server": "Gives this user elevated permissions with the REST API. Used for remote server credentials.",
            "is_superuser": "Gives this user full administrator permissions.",
        }


#TODO: Find a way to display read-only fields
class AuthorChangeForm(UserChangeForm):
    """
    Custom form for editing users
    """
    class Meta:
        model = Author
        fields = ("username", "password", "first_name", "last_name", "email", "github", "is_active", "is_server", "is_superuser",)
        exclude = ("groups", "user_permissions",)
        help_texts = {
            "is_active": "Whether or not a user has permission to log-in.",
            "is_server": "Gives this user elevated permissions with the REST API. Used for remote server credentials.",
            "is_superuser": "Gives this user full administrator permissions.",
        }


class AuthorAdmin(UserAdmin):
    """
    Author model representation in Django admin
    """
    model = Author
    form = AuthorChangeForm
    add_form = AuthorCreationForm
    list_display = ("username", "email", "id", "is_active", "is_server",)
    list_filter = ("is_active", "is_server",)
    fieldsets = (
        (None, {'fields': ('username', 'email', 'id', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'github')}),
        ('Permissions', {'fields': ('is_active', 'is_server', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )


class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "id", "author", "visibility", "unlisted",)
    list_filter = ("author", "visibility", "unlisted")


# Set some admin site variables
admin.site.site_header = "Social Distribution Project Admin"
admin.site.site_title = "Social Distribution Project Admin"
admin.site.index_title = "Welcome to the administration portal"

# Hide Groups since we only have one user group
admin.site.unregister(Group)

# Register our models with the admin site
admin.site.register(Author, AuthorAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(PostCategory, DefaultAdmin)
admin.site.register(Comment, DefaultAdmin)
admin.site.register(Followers, DefaultAdmin)
admin.site.register(LikedPost, DefaultAdmin)


