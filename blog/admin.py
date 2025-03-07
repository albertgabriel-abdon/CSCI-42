from django.contrib import admin

# Register your models here.
from .models import Article, ArticleCategory, Comment, Recipe, MealPlanRecipe

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

class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'difficulty', 'servings', 'created_by', 'created_on', 'is_published', 'rating')
    list_filter = ('category', 'difficulty', 'is_published', 'created_on')
    search_fields = ('name', 'description', 'created_by__username')
    ordering = ['-created_on']
    readonly_fields = ('created_on', 'updated_on')

class MealPlanRecipeAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'meal_plan', 'scheduled_date')
    list_filter = ('scheduled_date',)
    search_fields = ('recipe__name', 'meal_plan__name')

admin.site.register(Recipe, RecipeAdmin)
admin.site.register(MealPlanRecipe, MealPlanRecipeAdmin)
