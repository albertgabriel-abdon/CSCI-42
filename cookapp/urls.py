from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (HomeView, LoginView, 
                    MealPlanListView, 
                    UserMealPlanCreateView, MealPlanCreateView,
                    MealPlanDetailView,
                    MealPlanUpdateView, MealPlanDeleteView,
                    RecipeAddView, RecipeCreateView, UserRecipeListView,
                    CommunityPantryListView, CommunityPantryDetailView, CommunityPantryRequestView
                    
                    )
urlpatterns = [
    path('home', HomeView.as_view(), name='home'),
    path('accounts/login/', LoginView.as_view(), name='login'),
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),

    path('mealplans/', MealPlanListView.as_view(), name='mealplan_list'),

    path('community-pantry/', CommunityPantryListView.as_view(), name='community_pantry_list'),
    path('community_pantry/<int:cp_pk>/', CommunityPantryDetailView.as_view(), name='community_pantry_detail'),
    path('community-pantry/request/', CommunityPantryRequestView.as_view(), name='community_pantry_request'),

    path('cookapp/mealplan/<int:mealplan_pk>/', MealPlanDetailView.as_view(), name='mealplan_detail'),
    
    path('mealplans/create', UserMealPlanCreateView.as_view(), name='mealplans_create'),
    path('cookapp/mealplan/create/', MealPlanCreateView.as_view(), name='mealplan_create'),
    path('cookapp/mealplan/<int:mealplan_pk>/update/', MealPlanUpdateView.as_view(), name='mealplan_update'),
    path('cookapp/mealplan/<int:mealplan_pk>/delete/', MealPlanDeleteView.as_view(), name='mealplan_delete'),

    path('cookapp/mealplan/<int:mealplan_pk>/add-recipe/', RecipeAddView.as_view(), name='recipe_add'),
    path('recipe/new/', RecipeCreateView.as_view(), name='recipe_create'),
    path('recipe/new/<int:mealplan_pk>/', RecipeCreateView.as_view(), name='recipe_create'),
    path('recipes/', UserRecipeListView.as_view(), name='recipe_list'),
    
]

app_name = 'cookapp'
