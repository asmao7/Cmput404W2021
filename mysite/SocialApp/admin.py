from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import TextPost, ImagePost, Author, PostCategory, Comment

class DefaultAdmin(admin.ModelAdmin):
    # Default Admin Panel
    pass


class AuthorAdmin(UserAdmin):
    readonly_fields = ("id", "host", "url",)


admin.site.register(Author, AuthorAdmin)
admin.site.register(TextPost, DefaultAdmin)
admin.site.register(ImagePost, DefaultAdmin)
admin.site.register(PostCategory, DefaultAdmin)
admin.site.register(Comment, DefaultAdmin)