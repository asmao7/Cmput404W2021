from django.contrib import admin
from .models import TextPost, ImagePost, Author, PostCategory, Comment

class DefaultAdmin(admin.ModelAdmin):
   # Default Admin Panel
   pass

admin.site.register(TextPost, DefaultAdmin)
admin.site.register(ImagePost, DefaultAdmin)
admin.site.register(Author, DefaultAdmin)
admin.site.register(PostCategory, DefaultAdmin)
admin.site.register(Comment, DefaultAdmin)