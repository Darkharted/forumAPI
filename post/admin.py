from django.contrib import admin
import post
from post.models import Comment, Favorite, Post
from django.db.models.aggregates import Count

admin.site.register(Favorite)
admin.site.register(Comment)


def enable_moderated(modeladmin, request, queryset):
    queryset.update(moderated='True')
# enable_moderated.short_description = "Enable Moderated"


def disable_moderated(modeladmin, request, queryset):
    queryset.update(moderated='False')




class Comment(admin.TabularInline):
    model = Comment



@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("pk","title","author", "moderated","short_description","created","get_comment_count" )
    search_fields = ('title', "description")
    list_filter = ('author',)
    actions = [enable_moderated, disable_moderated]
    inlines = [Comment]
    list_editable = ['moderated']


    def get_comment_count(self, comments_count):
        return comments_count.comments.count()

