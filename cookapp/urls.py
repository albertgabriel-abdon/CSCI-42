from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (HomeView, LoginView, 
                    MealPlanListView, 
                    UserMealPlanCreateView, MealPlanCreateView,
                    MealPlanDetailView,
                    MealPlanUpdateView, MealPlanDeleteView,
                    RecipeAddView, RecipeCreateView, UserRecipeListView,
                    CommunityPantryListView, CommunityPantryDetailView, CommunityPantryRequestView,
                    GroceryListView, GroceryListCreateView, GroceryListUpdateView,
                    InventoryListView, InventoryCreateView, InventoryDeleteView, InventoryDetailView,
                    RecipeEditView, RecipeDetailView, RecipeDeleteView, AllRecipesView,
                    ClearGroceryListView
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
    path('recipes/<int:pk>/', RecipeDetailView.as_view(), name='recipe_detail'),
    path('recipes/<int:pk>/edit/', RecipeEditView.as_view(), name='recipe_update'),
    path('recipe/<int:pk>/delete/', RecipeDeleteView.as_view(), name='recipe_delete'),
    path('all-recipes/', AllRecipesView.as_view(), name='all_recipes'),
    

   path('inventory/', InventoryListView.as_view(), name='inventory_list'),
    path('inventory/create/', InventoryCreateView.as_view(), name='inventory_create'),
    path('inventory/<int:pk>/delete/', InventoryDeleteView.as_view(), name='inventory_delete'),
    path("inventory/<int:pk>/", InventoryDetailView.as_view(), name="inventory_detail"),


    path("grocerylist/", GroceryListView.as_view(), name="grocery_list"),
    path('grocery/add/', GroceryListCreateView.as_view(), name='grocery_list_add'),
    path('grocery/edit/<int:item_pk>/', GroceryListUpdateView.as_view(), name='grocery_list_update'),
    path('grocery/clear/', ClearGroceryListView.as_view(), name='grocery_list_clear'),
    
]

app_name = 'cookapp'
