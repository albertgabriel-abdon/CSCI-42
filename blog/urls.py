from django.urls import path
from .views import (RecipeDetailView, ArticleListView, 
                    MealPlanListView, 
                    MealPlanDetailView, MealPlanCreateView, 
                    MealPlanUpdateView, MealPlanDeleteView,
                    RecipeUpdateView, RecipeDeleteView,
                    RecipeAddView, RecipeAddFormView,
                    RecipeCreateView, InventoryCreateView,InventoryDeleteView, 
                    InventoryListView, IngredientCreateView,
                    InventoryDetailView, GroceryListView

                    )
urlpatterns = [
    path('blog/articles',ArticleListView.as_view(), name='article_site'),
    path('blog/recipe/<int:pk>/', RecipeDetailView.as_view(), name='recipe_detail'),

    path('blog/mealplans/', MealPlanListView.as_view(), name='mealplan_list'),
    path('blog/mealplan/<int:mealplan_pk>/', MealPlanDetailView.as_view(), name='mealplan_detail'),

    path('blog/mealplan/create/', MealPlanCreateView.as_view(), name='mealplan_create'),
    path('blog/mealplan/<int:mealplan_pk>/update/', MealPlanUpdateView.as_view(), name='mealplan_update'),
    path('blog/mealplan/<int:mealplan_pk>/delete/', MealPlanDeleteView.as_view(), name='mealplan_delete'),
    path('blog/mealplan/<int:mealplan_pk>/add-recipe/', RecipeAddView.as_view(), name='recipe_add'),
    path('blog/mealplan/<int:mealplan_pk>/add-recipe-form/', RecipeAddFormView.as_view(), name='recipe_add_form'),
    path('blog/recipe/<int:pk>/update/', RecipeUpdateView.as_view(), name='recipe_update'),
    path('blog/recipe/<int:pk>/delete/', RecipeDeleteView.as_view(), name='recipe_delete'),

    path('recipe/new/<int:mealplan_pk>/', RecipeCreateView.as_view(), name='recipe_create'),

    path('inventory/', InventoryListView.as_view(), name='inventory_list'),
    path('inventory/create/', InventoryCreateView.as_view(), name='inventory_create'),
    path('inventory/<int:pk>/delete/', InventoryDeleteView.as_view(), name='inventory_delete'),
    path("inventory/<int:pk>/", InventoryDetailView.as_view(), name="inventory_detail"),

    path('ingredient/new/', IngredientCreateView.as_view(), name='ingredient_create'),
    path("grocerylist/", GroceryListView.as_view(), name="grocery_list"),


]


app_name = 'blog'
