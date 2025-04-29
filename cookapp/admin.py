from django.contrib import admin

# Register your models here.
from .models import (Recipe, GroceryList,
                     MealPlanRecipe, MealPlan, Ingredient, 
                     RecipeIngredient, NutritionalInformation, 
                     InventoryManager)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'difficulty', 'servings', 'created_by', 'created_on', 'is_published', 'rating')
    list_filter = ('category', 'difficulty', 'is_published', 'created_on')
    search_fields = ('name', 'description', 'created_by__username')
    ordering = ['-created_on']
    readonly_fields = ('created_on', 'updated_on')

class MealPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'start_date', 'status', 'visibility')
    list_filter = ('status', 'visibility', 'start_date')
    search_fields = ('name', 'user__username')

class MealPlanRecipeAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'meal_plan', 'scheduled_date')
    list_filter = ('scheduled_date',)
    search_fields = ('recipe__name', 'meal_plan__name')

class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit', 'estimated_expiration_date')
    search_fields = ('name',)

class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'quantity')
    search_fields = ('recipe__name', 'ingredient__name')

class NutritionalInformationAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'calories', 'proteins', 'fat', 'carbs', 'fiber')
    search_fields = ('ingredient__name',)

class InventoryManagerAdmin(admin.ModelAdmin):
    list_display = ('user', 'ingredient', 'quantity', 'is_buyer')
    list_filter = ('is_buyer',)
    search_fields = ('user__username', 'ingredient__name')

class GroceryListAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'user', 'status', 'updated_on')
    list_filter = ('status', 'updated_on')
    search_fields = ('ingredient__name', 'user__username')

admin.site.register(GroceryList, GroceryListAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(MealPlan, MealPlanAdmin)
admin.site.register(MealPlanRecipe, MealPlanRecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(NutritionalInformation, NutritionalInformationAdmin)
admin.site.register(InventoryManager, InventoryManagerAdmin)
