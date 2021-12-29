from django.contrib import admin
from post.models import Comment, Favorite, Post

admin.site.register(Favorite)


class Comment(admin.StackedInline):
    model = Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title","author","pk", "moderated","description","created")
    search_fields = ('title', "description")
    list_filter = ('author',)
    date_hierarchy = ("created")    
    inlines = [Comment]


