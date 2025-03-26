from django.utils.timezone import now
from datetime import date, timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from django.db import IntegrityError
from django.views.generic import TemplateView
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.models import User

from django.views.generic.edit import FormView
from django.views.generic import DeleteView, CreateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import (Article, ArticleCategory, 
                     Comment, Recipe, MealPlan,
                     InventoryManager, Ingredient, 
                     NutritionalInformation, GroceryList,
                     UserRequest
                     )
from .forms import (ArticleForm, CommentForm, 
                    RecipeForm, RecipeAddForm, 
                    IngredientForm, InventoryEditForm,
                    MealPlanForm)

from django.shortcuts import get_object_or_404, redirect
from django.views import View

from .models import MealPlan, Recipe, MealPlanRecipe

from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView
from .models import Ingredient, UserRequest

from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from .models import Recipe

class UserMealPlanCreateView(CreateView):
    model = MealPlan
    form_class = MealPlanForm
    template_name = 'meal_plan/create_mealplan.html'
    success_url = reverse_lazy('blog:mealplans_list') 

    def form_valid(self, form):
        if not form.cleaned_data.get('start_date'):
            form.instance.start_date = datetime.today().date()
        
        form.instance.user = self.request.user
        response = super().form_valid(form)
        return response

class UserMealPlanListView(LoginRequiredMixin, ListView):
    model = MealPlan
    template_name = 'meal_plan/meal_plan_list_view.html'
    context_object_name = 'mealplans'

    def get_queryset(self):
        query = self.request.GET.get('q')
        user = self.request.user

        queryset = MealPlan.objects.filter(
            Q(visibility='public') | Q(user=user)
        )
        
        if query:
            queryset = queryset.filter(name__icontains=query)
        
        return queryset.order_by('-start_date')
    
class UserRecipeListView(LoginRequiredMixin, ListView):
    model = Recipe
    template_name = 'recipe_list_view.html'
    context_object_name = 'user_recipes' 
    
    def get_queryset(self):
        query = self.request.GET.get('q')
        queryset = Recipe.objects.filter(created_by=self.request.user)
        if query:
            queryset = queryset.filter(name__icontains=query)
        return queryset
    
class CommunityPantryRequestView(TemplateView):
    template_name = "community_pantry/community_pantry_request.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ingredients'] = Ingredient.objects.all() 
        return context

    def post(self, request, *args, **kwargs):
        ingredient_id = request.POST.get('ingredient')
        quantity = request.POST.get('quantity')

        try:
            ingredient = Ingredient.objects.get(id=ingredient_id)
        except Ingredient.DoesNotExist:
            return render(request, self.template_name, {
                'error': 'Invalid ingredient selection',
                'ingredients': Ingredient.objects.all(),  
            })

        UserRequest.objects.create(
            user=request.user,
            ingredient=ingredient,
            quantity=int(quantity),
            distance=10,  
        )

        return redirect(reverse('blog:community_pantry_list'))

class CommunityPantryDetailView(DetailView):
    model = UserRequest
    template_name = "community_pantry/community_pantry_detail.html"
    context_object_name = "user_request"

    def get_object(self):
        cp_pk = self.kwargs.get("cp_pk")
        return UserRequest.objects.get(pk=cp_pk)

    def post(self, request, *args, **kwargs):
        user_request = self.get_object()

        # add logic here for transaction stuff
        user_request.delete() 
        return redirect(reverse('community_pantry_list'))

class CommunityPantryListView(TemplateView):
    template_name = "community_pantry/community_pantry_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_requests'] = UserRequest.objects.all()
        return context

class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Community Pantry - Prep & Plate"
        return context

class GroceryListView(ListView):
    model = Ingredient
    template_name = "grocery_list.html"
    context_object_name = "ingredients" 
    paginate_by = 20  

    def get_queryset(self):
        return Ingredient.objects.filter(
            inventorymanager__quantity__gt=0
        ).distinct() 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        inventory_data = InventoryManager.objects.filter(
            quantity__gt=0 
        )

        context['inventory_data'] = inventory_data
        return context

class InventoryDetailView(View):
    template_name = "inventory_detail.html"

    def get(self, request, pk):
        inventory_item = get_object_or_404(InventoryManager, pk=pk, user=request.user)
        return render(request, self.template_name, {"inventory_item": inventory_item})

    def post(self, request, pk):
        inventory_item = get_object_or_404(InventoryManager, pk=pk, user=request.user)
        
        inventory_item.quantity = request.POST.get("quantity")
        inventory_item.is_buyer = request.POST.get("is_buyer") == "False"
        inventory_item.save()

        messages.success(request, "Inventory updated successfully!")
        return redirect("blog:inventory_detail", pk=pk)

class InventoryDeleteView(LoginRequiredMixin, DeleteView):
    model = InventoryManager
    success_url = reverse_lazy("blog:inventory_list")  
    template_name = "inventory_confirm_delete.html"

class IngredientCreateView(CreateView):
    model = Ingredient
    form_class = IngredientForm
    template_name = "ingredient_create.html"

    def form_valid(self, form):
        ingredient = form.save()

        NutritionalInformation.objects.create(
            ingredient=ingredient,
            calories=self.request.POST.get("calories"),
            proteins=self.request.POST.get("proteins"),
            fat=self.request.POST.get("fat"),
            carbs=self.request.POST.get("carbs"),
            fiber=self.request.POST.get("fiber"),
        )

        messages.success(self.request, "Ingredient created successfully!")
        return redirect(reverse('inventory_list'))

class InventoryListView(View):
    def get(self, request):
        inventory_items = InventoryManager.objects.filter(user=request.user)
        return render(request, 'inventory_manager.html', {"inventory_items": inventory_items})

class InventoryCreateView(View):
    def post(self, request):
        ingredient_name = request.POST.get("ingredient_name")
        unit = request.POST.get("unit")
        estimated_expiration_date = request.POST.get("estimated_expiration_date")
        calories = request.POST.get("calories")
        proteins = request.POST.get("proteins")
        fat = request.POST.get("fat")
        carbs = request.POST.get("carbs")
        fiber = request.POST.get("fiber")

        ingredient, created = Ingredient.objects.get_or_create(
            name=ingredient_name,
            defaults={"unit": unit, "estimated_expiration_date": estimated_expiration_date}
        )

        NutritionalInformation.objects.update_or_create(
            ingredient=ingredient,
            defaults={
                "calories": calories,
                "proteins": proteins,
                "fat": fat,
                "carbs": carbs,
                "fiber": fiber,
            }
        )

        try:
            inventory_item, created = InventoryManager.objects.get_or_create(
                user=request.user,
                ingredient=ingredient
            )

            if created:
                messages.success(request, "Ingredient added successfully!")
            else:
                messages.warning(request, "This ingredient is already in your inventory.")

        except IntegrityError:
            messages.error(request, "You already have this ingredient in your inventory.")

        return redirect("blog:inventory_list")

class InventoryEditView(View):
    def get(self, request, pk):
        """Handle GET request to display the edit form."""
        inventory_item = get_object_or_404(InventoryManager, pk=pk, user=request.user)
        return render(request, "inventory_edit.html", {"inventory_item": inventory_item})

    def post(self, request, pk):
        """Handle POST request to update the inventory item."""
        inventory_item = get_object_or_404(InventoryManager, pk=pk, user=request.user)

        quantity = request.POST.get("quantity")
        is_buyer = request.POST.get("is_buyer") == "True"

        inventory_item.quantity = quantity
        inventory_item.is_buyer = is_buyer
        inventory_item.save()

        messages.success(request, "Inventory item updated successfully!")
        return redirect("blog:inventory_list")

class InventoryDeleteView(View):
    def post(self, request, pk):
        inventory_item = get_object_or_404(InventoryManager, pk=pk, user=request.user)
        inventory_item.delete()
        messages.success(request, "Item deleted successfully!")
        return redirect("blog:inventory_list")

class RecipeAddView(View):
    def post(self, request, mealplan_pk):
        meal_plan = get_object_or_404(MealPlan, pk=mealplan_pk, user=request.user)  
        recipe_id = request.POST.get("recipe_id")  
        scheduled_dates_raw = request.POST.get("scheduled_dates", "").strip() 

        if not recipe_id:
            messages.error(request, "Recipe ID is required.")
            return redirect("blog:mealplan_detail", mealplan_pk=mealplan_pk)

        recipe = get_object_or_404(Recipe, pk=recipe_id)

        if not scheduled_dates_raw:
            messages.error(request, "No date added. Please select at least one date.")
            return redirect("blog:mealplan_detail", mealplan_pk=mealplan_pk)

        try:
            scheduled_dates = [
                datetime.strptime(date.strip(), "%Y-%m-%d").date()
                for date in scheduled_dates_raw.split(",") if date.strip()
            ]
        except ValueError:
            messages.error(request, "Invalid date format. Please select a valid date.")
            return redirect("blog:mealplan_detail", mealplan_pk=mealplan_pk)

        added_dates = []
        skipped_dates = []

        for scheduled_date in scheduled_dates:
            if MealPlanRecipe.objects.filter(meal_plan=meal_plan, recipe=recipe, scheduled_date=scheduled_date).exists():
                skipped_dates.append(scheduled_date)
            else:
                MealPlanRecipe.objects.create(meal_plan=meal_plan, recipe=recipe, scheduled_date=scheduled_date)
                added_dates.append(scheduled_date)

        if added_dates:
            messages.success(request, f"Recipe added for: {', '.join(str(d) for d in added_dates)}.")
        if skipped_dates:
            messages.warning(request, f"Skipped duplicates for: {', '.join(str(d) for d in skipped_dates)}.")

        return redirect("blog:mealplan_detail", mealplan_pk=meal_plan.pk)

    
class RecipeAddFormView(FormView):
    template_name = "recipe_add_form.html"
    form_class = RecipeAddForm

    def post(self, request, pk):
        meal_plan_id = request.POST.get("meal_plan")
        return redirect("blog:recipe_add", pk=meal_plan_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        meal_plan = get_object_or_404(MealPlan, pk=self.kwargs["pk"])
        context["meal_plan"] = meal_plan
        context["recipes"] = Recipe.objects.all()
        return context

    def form_valid(self, form):
        """Handle the form submission."""
        meal_plan = get_object_or_404(MealPlan, pk=self.kwargs["pk"])
        recipe = form.cleaned_data["recipe"]
        scheduled_date = form.cleaned_data["scheduled_date"]

        existing_entry = MealPlanRecipe.objects.filter(
            meal_plan=meal_plan, recipe=recipe, scheduled_date=scheduled_date
        ).exists()

        if existing_entry:
            messages.warning(self.request, "This recipe is already scheduled for this date.")
        else:
            MealPlanRecipe.objects.create(
                meal_plan=meal_plan, recipe=recipe, scheduled_date=scheduled_date
            )
            messages.success(self.request, "Recipe successfully added to the meal plan!")

        return redirect("blog:mealplan_detail", pk=meal_plan.pk)


class MealPlanListView(ListView):
    model = MealPlan
    template_name = "mealplan_list.html"
    context_object_name = "mealplans"

    
class MealPlanDetailView(DetailView):
    model = MealPlan
    template_name = "mealplan_detail.html"
    context_object_name = "mealplan"

    def get_object(self):
        return get_object_or_404(MealPlan, pk=self.kwargs["mealplan_pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recipes"] = Recipe.objects.all()
        return context

    def post(self, request, *args, **kwargs):
        """Handles updating a scheduled date of a recipe in the meal plan while preventing duplicates."""
        meal_plan = self.get_object()
        meal_plan_recipe_id = request.POST.get("meal_plan_recipe_id")
        scheduled_date = request.POST.get("scheduled_date")

        if not meal_plan_recipe_id or not scheduled_date:
            messages.error(request, "Invalid request. Please select a valid date.")
            return redirect("blog:mealplan_detail", mealplan_pk=meal_plan.pk)

        try:
            meal_plan_recipe = MealPlanRecipe.objects.get(pk=meal_plan_recipe_id, meal_plan=meal_plan)
            new_scheduled_date = datetime.strptime(scheduled_date, "%Y-%m-%d").date()

            duplicate_exists = MealPlanRecipe.objects.filter(
                meal_plan=meal_plan, recipe=meal_plan_recipe.recipe, scheduled_date=new_scheduled_date
            ).exists()

            if duplicate_exists:
                messages.error(request, f"This recipe is already scheduled for {new_scheduled_date}.")
            else:
                meal_plan_recipe.scheduled_date = new_scheduled_date
                meal_plan_recipe.save()
                messages.success(request, "Scheduled date updated successfully!")

        except MealPlanRecipe.DoesNotExist:
            messages.error(request, "Meal plan recipe not found.")

        return redirect("blog:mealplan_detail", mealplan_pk=meal_plan.pk)


class MealPlanCreateView(CreateView):
    model = MealPlan
    #form_class = MealPlanForm
    template_name = "mealplan_form.html"
    fields = ["name", "start_date", "status", "visibility"]
    
    def form_valid(self, form):
        form.instance.user = self.request.user 
        #for user save stuff
        return super().form_valid(form)

class MealPlanUpdateView(UpdateView):
    model = MealPlan
    #form_class = MealPlanForm
    template_name = "mealplan_form.html"
    fields = ["name", "start_date", "status", "visibility"]

    def get_object(self, queryset=None):
        return get_object_or_404(MealPlan, pk=self.kwargs["mealplan_pk"])

class MealPlanDeleteView(DeleteView):
    model = MealPlan
    template_name = "mealplan_confirm_delete.html"
    success_url = reverse_lazy("blog:mealplan_list")

    def get_object(self, queryset=None):
        return get_object_or_404(MealPlan, pk=self.kwargs["mealplan_pk"])


class RecipeDetailView(DetailView):
    model = Recipe
    template_name = "recipe_detail.html"
    context_object_name = 'recipe'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_authenticated:
            meal_plan_recipes = MealPlanRecipe.objects.filter(recipe=self.object, meal_plan__user=user)
            meal_plans = MealPlan.objects.filter(user=user) 
        else:
            meal_plan_recipes = MealPlanRecipe.objects.none()
            meal_plans = MealPlan.objects.none()

        default_scheduled_date = now().date() + timedelta(days=30)  

        context["meal_plan_recipes"] = meal_plan_recipes
        context["meal_plans"] = meal_plans
        context["default_scheduled_date"] = default_scheduled_date

        return context

    def post(self, request, *args, **kwargs):
        #Edit Date forgot to work
        """Handles adding a recipe with multiple scheduled dates to a meal plan."""
        recipe = self.get_object()
        meal_plan_id = request.POST.get("meal_plan_id")
        scheduled_dates = request.POST.get("scheduled_dates")  

        if not meal_plan_id:
            messages.error(request, "Please select a meal plan.")
            return redirect("blog:recipe_detail", pk=recipe.pk)

        meal_plan = get_object_or_404(MealPlan, pk=meal_plan_id, user=request.user)

        if not scheduled_dates:
            messages.error(request, "Please select at least one date.")
            return redirect("blog:recipe_detail", pk=recipe.pk)

        scheduled_dates = scheduled_dates.split(",")  
        scheduled_dates = [datetime.strptime(date.strip(), "%Y-%m-%d").date() for date in scheduled_dates]

        added_count = 0
        skipped_count = 0

        for scheduled_date in scheduled_dates:
            meal_plan_recipe = MealPlanRecipe.objects.filter(
                meal_plan=meal_plan, recipe=recipe, scheduled_date=scheduled_date
            ).first()

            if meal_plan_recipe:
                skipped_count += 1  
            else:
                MealPlanRecipe.objects.create(meal_plan=meal_plan, recipe=recipe, scheduled_date=scheduled_date)
                added_count += 1

        if added_count > 0:
            messages.success(request, f"Recipe added to meal plan on {added_count} date(s) successfully!")
        if skipped_count > 0:
            messages.warning(request, f"Skipped {skipped_count} date(s) because they were already scheduled.")

        return redirect("blog:recipe_detail", pk=recipe.pk)


    #context_obj_name is relevant
    #context['recipes'] = Recipe.objects.all()
    # #context['recipes'] = Recipe.objects.filter(is_published=True) for site itself
    
class RecipeCreateView(LoginRequiredMixin, View):
    def get(self, request, mealplan_pk=None):
        return render(request, 'recipe_form.html', {
            "category_choices": Recipe.CATEGORY_CHOICES,
            "difficulty_choices": Recipe.DIFFICULTY_CHOICES,
            "mealplan_pk": mealplan_pk
        })

    def post(self, request, mealplan_pk=None):  
        name = request.POST.get("name")
        description = request.POST.get("description")
        category = request.POST.get("category")
        difficulty = request.POST.get("difficulty")
        preparation_time = request.POST.get("preparation_time")
        cook_time = request.POST.get("cook_time")
        servings = request.POST.get("servings")
        instructions = request.POST.get("instructions")

        if not all([name, description, category, difficulty, preparation_time, cook_time, servings, instructions]):
            messages.error(request, "All fields are required.")
            return redirect("blog:recipe_create", mealplan_pk=mealplan_pk)

        recipe = Recipe.objects.create(
            name=name,
            description=description,
            category=category,
            difficulty=difficulty,
            preparation_time=preparation_time,
            cook_time=cook_time,
            servings=servings,
            instructions=instructions,
            created_by=request.user
        )

        messages.success(request, "Recipe created successfully!")

        if mealplan_pk:
            return redirect("blog:mealplan_detail", mealplan_pk=mealplan_pk)

        return redirect(recipe.get_absolute_url())
    

class RecipeUpdateView(LoginRequiredMixin, UpdateView):
    model = Recipe
    form_class = RecipeForm
    template_name = "recipe_form.html"

class RecipeDeleteView(LoginRequiredMixin, DeleteView):
    model = Recipe
    success_url = reverse_lazy("blog:article_site")
    template_name = "recipe_confirm_delete.html"
#################################################################
    
class ArticleListView(ListView):
    model = Article
    template_name = 'article_site.html' 

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_category'] = int(self.request.GET.get('category', 0))
        context['is_main'] = True  
        context['category'] = ArticleCategory.objects.all()
        context['form'] = ArticleForm()
        return context
    
    def post(self, request, *args, **kwargs):
        
        if 'reset' in request.GET:
            return self.get(request, *args, **kwargs, selected_category=0)

        else:
            articles = Article()
            articles.title = request.POST['article_title']
            articles.author = request.user
            articles.entry = request.POST.get('article_entry')
            articles.category = ArticleCategory.objects.get(pk=request.POST.get('category'))
            articles.header_image = request.POST.get('header_image')
            articles.save()
            
            return self.get(request, *args, **kwargs)
         
