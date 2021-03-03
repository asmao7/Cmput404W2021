from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import Post, Author, PostCategory, Comment

class DefaultAdmin(admin.ModelAdmin):
    # Default Admin Panel
    pass


class AuthorCreationForm(UserCreationForm):
    # Custom form for creating new users
    class Meta:
        model = Author
        fields = UserCreationForm.Meta.fields + ("display_name", "github",)


#TODO: Find a way to display read-only fields
class AuthorChangeForm(UserChangeForm):
    # Custom form for editing users
    class Meta:
        model = Author
        fields = ("username", "password", "first_name", "last_name", "display_name", "email", "github", "is_active", "is_staff", "is_superuser", "groups", "user_permissions",)


class AuthorAdmin(UserAdmin):
    # Admin User Admin Panel
    model = Author
    form = AuthorChangeForm


admin.site.register(Author, AuthorAdmin)
admin.site.register(Post, DefaultAdmin)
admin.site.register(PostCategory, DefaultAdmin)
admin.site.register(Comment, DefaultAdmin)