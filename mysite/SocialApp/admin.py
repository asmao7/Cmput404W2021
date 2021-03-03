from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import TextPost, ImagePost, Author, PostCategory, Comment

class DefaultAdmin(admin.ModelAdmin):
    # Default Admin Panel
    pass


# TODO: This should be a UserAdmin, or emulate one, but I can't figure out how
#       to display read-only fields without using ModelAdmin
class AuthorAdmin(admin.ModelAdmin):
    # Custom admin panel for Authors
    readonly_fields = ("id", "host", "url",)


admin.site.register(Author, AuthorAdmin)
admin.site.register(TextPost, DefaultAdmin)
admin.site.register(ImagePost, DefaultAdmin)
admin.site.register(PostCategory, DefaultAdmin)
admin.site.register(Comment, DefaultAdmin)