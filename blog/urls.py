from django.urls import path
from .views import (RecipeDetailView, ArticleListView, 
                    MealPlanListView, 
                    MealPlanDetailView, MealPlanCreateView, 
                    MealPlanUpdateView, MealPlanDeleteView,
                    RecipeUpdateView, RecipeDeleteView,
                    RecipeAddView, RecipeAddFormView
                    )
urlpatterns = [
    path('blog/articles',ArticleListView.as_view(), name='article_site'),
    path('blog/recipe/<int:pk>/', RecipeDetailView.as_view(), name='recipe_detail'),

    path('blog/mealplans/', MealPlanListView.as_view(), name='mealplan_list'),
    path('blog/mealplan/<int:pk>/', MealPlanDetailView.as_view(), name='mealplan_detail'),
    path('blog/mealplan/create/', MealPlanCreateView.as_view(), name='mealplan_create'),
    path('blog/mealplan/<int:pk>/update/', MealPlanUpdateView.as_view(), name='mealplan_update'),
    path('blog/mealplan/<int:pk>/delete/', MealPlanDeleteView.as_view(), name='mealplan_delete'),

    path('blog/mealplan/<int:pk>/add-recipe/', RecipeAddView.as_view(), name='recipe_add'),
    path('blog/mealplan/<int:pk>/add-recipe-form/', RecipeAddFormView.as_view(), name='recipe_add_form'),
    path('blog/recipe/<int:pk>/update/', RecipeUpdateView.as_view(), name='recipe_update'),
    path('blog/recipe/<int:pk>/delete/', RecipeDeleteView.as_view(), name='recipe_delete'),

]


app_name = 'blog'
