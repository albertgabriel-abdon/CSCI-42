from django.contrib import admin

# Register your models here.
from .models import Article, ArticleCategory, Comment

class ArticleInline(admin.StackedInline):
    model = Article
     
class ArticleCategoryAdmin(admin.ModelAdmin):
    inlines = [ArticleInline]
    
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'article', 'created_on')
    list_filter = ('created_on',)
    search_fields = ['author__username', 'article__title']


admin.site.register(Comment, CommentAdmin)
admin.site.register(ArticleCategory, ArticleCategoryAdmin)
admin.site.register(Article)
