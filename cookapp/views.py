from django.shortcuts import render, get_object_or_404, redirect
import random
from datetime import date
from datetime import datetime
from django.db import IntegrityError
from django.http import JsonResponse

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin

from django.urls import reverse_lazy
from django.urls import reverse

from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.views.generic import DeleteView, CreateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView

from accounts.forms import LoginForm
from .forms import (RecipeForm, RecipeAddForm, 
                    IngredientForm, InventoryEditForm,
                    MealPlanForm, EditMealPlanForm,
                    CreateRecipeForm, 
                    )

from django.db.models import Q
from .models import (Recipe, MealPlan,
                     InventoryManager, Ingredient, 
                     NutritionalInformation, GroceryList,
                    UserRequest, MealPlanRecipe, UserRequest
                    )

from django.views import View
from django.contrib.auth.decorators import login_not_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

##### KITCHEN/INVENTORY #####

class InventoryDetailView(View):
    template_name = "kitchen/inventory_detail.html"

    def get(self, request, pk):
        inventory_item = get_object_or_404(InventoryManager, pk=pk, user=request.user)
        return render(request, self.template_name, {"inventory_item": inventory_item})

    def post(self, request, pk):
        inventory_item = get_object_or_404(InventoryManager, pk=pk, user=request.user)
        
        inventory_item.quantity = request.POST.get("quantity")
        inventory_item.is_buyer = request.POST.get("is_buyer") == "False"
        inventory_item.save()

        messages.success(request, "Inventory updated successfully!")
        return redirect("cookapp:inventory_detail", pk=pk)

class InventoryListView(View):
    def get(self, request):
        inventory_items = InventoryManager.objects.filter(user=request.user)
        return render(request, 'kitchen/inventory_manager.html', {"inventory_items": inventory_items})

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

        return redirect("cookapp:inventory_list")

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
        return redirect("cookapp:inventory_list")

class InventoryDeleteView(View):
    def post(self, request, pk):
        inventory_item = get_object_or_404(InventoryManager, pk=pk, user=request.user)
        inventory_item.delete()
        messages.success(request, "Item deleted successfully!")
        return redirect("cookapp:inventory_list")

##### GROCERY ######

class GroceryListCreateView(CreateView):
    model = GroceryList
    template_name = 'grocery/grocery_list_add.html'
    success_url = reverse_lazy('cookapp:grocery_list_add')  
    fields = ['ingredient', 'quantity', 'status']

    def form_valid(self, form):
        form.instance.user = self.request.user

        ingredient_id = self.request.POST.get('ingredient')
        if ingredient_id:
            try:
                ingredient = Ingredient.objects.get(id=ingredient_id)
                form.instance.ingredient = ingredient
            except Ingredient.DoesNotExist:
                return redirect('cookapp:inventory_list')

        try:
            return super().form_valid(form)
        except IntegrityError:
            messages.error(self.request, "This ingredient is already in your grocery list.")
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ingredients'] = Ingredient.objects.all()
        return context


class ClearGroceryListView(View):
    def post(self, request, *args, **kwargs):
        GroceryList.objects.filter(user=request.user).delete()
        return redirect('cookapp:grocery_list')
    
class GroceryListUpdateView(UpdateView):
    model = GroceryList
    fields = ['ingredient', 'quantity', 'status']
    template_name = 'grocery/grocery_list_edit.html'  
    success_url = reverse_lazy('cookapp:grocery_list')

    def get_queryset(self):
        return GroceryList.objects.filter(user=self.request.user)

class GroceryListView(TemplateView):
    template_name = "grocery/grocery_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['grocery_items'] = GroceryList.objects.filter(
            user=self.request.user
        ).select_related('ingredient')

        context['ingredients'] = Ingredient.objects.filter(
            inventorymanager__quantity__gt=0,
            inventorymanager__user=self.request.user
        ).distinct()

        context['inventory_data'] = InventoryManager.objects.filter(
            quantity__gt=0,
            user=self.request.user
        )

        return context

class GroceryItemDeleteView(View):
    def post(self, request, pk):
        try:
            grocery_item = GroceryList.objects.get(pk=pk, user=request.user)
            grocery_item.delete()
            messages.success(request, "Item deleted successfully!")
        except GroceryList.DoesNotExist:
            messages.error(request, "Item not found.")
        except Exception as e:
            messages.error(request, f"Error deleting item: {str(e)}")
        
        return redirect('cookapp:grocery_list')

##### COMMUNITY PANTRY ####
    
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

        return redirect(reverse('cookapp:community_pantry_list'))

class CommunityPantryListView(TemplateView):
    template_name = "community_pantry/community_pantry_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_requests'] = UserRequest.objects.all()  # User requests for ingredients
        return context

    def post(self, request, *args, **kwargs):
        quantity_to_send = int(request.POST.get('quantity'))
        ingredient_id = request.POST.get('ingredient_id')
        user_request_id = request.POST.get('user_request_id')

        ingredient = get_object_or_404(Ingredient, pk=ingredient_id)
        user_request = get_object_or_404(UserRequest, pk=user_request_id)

        if user_request.user == request.user:
            messages.error(request, "You can't send ingredients to yourself.")
            return redirect('cookapp:community_pantry_list')

        try:
            sender_inventory = InventoryManager.objects.get(user=request.user, ingredient=ingredient)
        except InventoryManager.DoesNotExist:
            messages.error(request, "You don't have this ingredient in your inventory.")
            return redirect('cookapp:community_pantry_list')

        if sender_inventory.quantity >= quantity_to_send:
            sender_inventory.quantity -= quantity_to_send
            sender_inventory.save()

            recipient_inventory, created = InventoryManager.objects.get_or_create(
                user=user_request.user, ingredient=ingredient
            )

            recipient_inventory.quantity += quantity_to_send
            recipient_inventory.save()

            # Check if the request is fully satisfied
            if quantity_to_send >= user_request.quantity:
                user_request.delete()
                messages.success(request, f"You've sent {quantity_to_send} {ingredient.name}(s) to {user_request.user.username}! Their request has been fulfilled.")
            else:
                # Update the request with the remaining quantity needed
                user_request.quantity -= quantity_to_send
                user_request.save()
                messages.success(request, f"You've sent {quantity_to_send} {ingredient.name}(s) to {user_request.user.username}! They still need {user_request.quantity} more.")
        else:
            messages.error(request, "You don't have enough of this ingredient to send.")

        return redirect('cookapp:community_pantry_list')
    
class CommunityPantryDetailView(DetailView):
    model = UserRequest
    template_name = "community_pantry/community_pantry_detail.html"
    context_object_name = "user_request"

    def get_object(self):
        cp_pk = self.kwargs.get("cp_pk")
        return UserRequest.objects.get(pk=cp_pk)

    def post(self, request, *args, **kwargs):
        user_request = self.get_object()
        ingredient = user_request.ingredient
        quantity_requested = user_request.quantity

        if request.user == user_request.user:
            messages.error(request, "You cannot send ingredients to yourself.")
            return redirect(reverse('cookapp:community_pantry_list'))

        sender_inventory = InventoryManager.objects.filter(user=request.user, ingredient=ingredient).first()

        if not sender_inventory:
            messages.error(request, f"You don't have {ingredient.name} in your inventory.")
            return redirect(reverse('cookapp:community_pantry_list'))

        if sender_inventory.quantity < quantity_requested:
            messages.error(request, f"You don't have enough {ingredient.name} in your inventory.")
            return redirect(reverse('cookapp:community_pantry_list'))

        recipient_inventory, created = InventoryManager.objects.get_or_create(
            user=user_request.user,
            ingredient=ingredient,
            defaults={'quantity': 0}
        )

        sender_inventory.quantity -= quantity_requested
        recipient_inventory.quantity += quantity_requested

        sender_inventory.save()
        recipient_inventory.save()

        messages.success(request, f"Successfully sent {quantity_requested} {ingredient.name} to {user_request.user.username}!")
        user_request.delete()
        return redirect(reverse('cookapp:community_pantry_list'))

##### RECIPE #####

class AllRecipesView(ListView):
    model = Recipe
    template_name = 'recipe/all_recipe.html'
    context_object_name = 'all_recipes'
    paginate_by = 10  

    def get_queryset(self):
        queryset = Recipe.objects.all()

        query = self.request.GET.get('q', '')
        if query:
            queryset = queryset.filter(name__icontains=query)

        return queryset

class RecipeDeleteView(LoginRequiredMixin, DeleteView):
    model = Recipe
    success_url = reverse_lazy('cookapp:recipe_list')
    template_name = 'recipe/confirm_delete.html'

    def get_queryset(self):
        return self.model.objects.filter(created_by=self.request.user)

class RecipeDetailView(DetailView):
    model = Recipe
    template_name = 'recipe/recipe_detail.html'
    context_object_name = 'recipe'

class UserRecipeListView(LoginRequiredMixin, ListView):
    model = Recipe
    template_name = 'recipe/recipe_listview.html'
    context_object_name = 'user_recipes' 

    def get_queryset(self):

        query = self.request.GET.get('q')
        queryset = Recipe.objects.filter(created_by=self.request.user)
        if query:
            queryset = queryset.filter(name__icontains=query)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        today = date.today()
        all_recipes = Recipe.objects.all()
        
        if all_recipes:
            recipe_of_the_day = random.choice(all_recipes)
        else:
            recipe_of_the_day = None

        context['recipe_of_the_day'] = recipe_of_the_day
        return context

class RecipeCreateView(LoginRequiredMixin, View):
    form_class = CreateRecipeForm

    def get(self, request, mealplan_pk=None):
        form = self.form_class()
        return render(request, 'recipe/create_recipe.html', {
            'form': form,
            'category_choices': Recipe.CATEGORY_CHOICES,
            'difficulty_choices': Recipe.DIFFICULTY_CHOICES,
            'mealplan_pk': mealplan_pk
        })

    def post(self, request, mealplan_pk=None):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            if mealplan_pk:
                recipe.meal_plan_id = mealplan_pk
            recipe.created_by = request.user
            recipe.save()

            messages.success(request, "Recipe created successfully!")

            if mealplan_pk:
                return redirect("cookapp:mealplan_detail", mealplan_pk=mealplan_pk)

            return redirect("cookapp:recipe_list")
        else:
            messages.error(request, "All fields are required.")
            return render(request, 'recipe/create_recipe.html', {
                'form': form,
                'category_choices': Recipe.CATEGORY_CHOICES,
                'difficulty_choices': Recipe.DIFFICULTY_CHOICES,
                'mealplan_pk': mealplan_pk
            })

class RecipeEditView(LoginRequiredMixin, UpdateView):
    model = Recipe
    form_class = CreateRecipeForm
    template_name = 'recipe/edit_recipe.html'
    success_url = reverse_lazy('cookapp:recipe_list')

    def get_object(self, queryset=None):
        return get_object_or_404(Recipe, pk=self.kwargs['pk'], created_by=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_choices'] = Recipe.CATEGORY_CHOICES
        context['difficulty_choices'] = Recipe.DIFFICULTY_CHOICES
        return context
    
class RecipeAddView(View):
   def post(self, request, mealplan_pk):
            meal_plan = get_object_or_404(MealPlan, pk=mealplan_pk, user=request.user)
            recipe_id = request.POST.get("recipe_id")  
            scheduled_dates_raw = request.POST.get("scheduled_dates", "").strip() 

            if not recipe_id:
                messages.error(request, "Recipe ID is required.")
                return redirect("cookapp:mealplan_detail", mealplan_pk=mealplan_pk)

            recipe = get_object_or_404(Recipe, pk=recipe_id)

            if not scheduled_dates_raw:
                messages.error(request, "No date added. Please select at least one date.")
                return redirect("cookapp:mealplan_detail", mealplan_pk=mealplan_pk)

            try:
                scheduled_dates = [
                    datetime.strptime(date.strip(), "%Y-%m-%d").date()
                    for date in scheduled_dates_raw.split(",") if date.strip()
                ]
            except ValueError:
                messages.error(request, "Invalid date format. Please select a valid date.")
                return redirect("cookapp:mealplan_detail", mealplan_pk=mealplan_pk)

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

            return redirect("cookapp:mealplan_detail", mealplan_pk=meal_plan.pk)
##### MEALPLAN #####

class MealPlanUpdateView(UpdateView):
    model = MealPlan
    form_class = EditMealPlanForm
    template_name = "meal_plan/edit_meal_plan.html"
    #fields = ["name", "start_date", "status", "visibility"]

    def get_object(self, queryset=None):
        return get_object_or_404(MealPlan, pk=self.kwargs["mealplan_pk"])

class MealPlanDeleteView(DeleteView):
    model = MealPlan
    template_name = "meal_plan/mealplan_confirm_delete.html"
    success_url = reverse_lazy("cookapp:mealplan_list")

    def get_object(self, queryset=None):
        return get_object_or_404(MealPlan, pk=self.kwargs["mealplan_pk"])
    
class MealPlanDetailView(DetailView):
    model = MealPlan
    template_name = "meal_plan/mealplan_detail.html"
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

        if 'save_meal_plan' in request.POST:
            if meal_plan.user == request.user:
                messages.info(request, "You can't save your own meal plan.")
            elif request.user in meal_plan.saved_by.all():
                messages.info(request, "You've already saved this meal plan.")
            else:
                meal_plan.saved_by.add(request.user)
                messages.success(request, "Meal plan saved!")
            return redirect("cookapp:mealplan_list") 
        
        if 'unsave_meal_plan' in request.POST:
            if meal_plan.user == request.user:
                messages.info(request, "You can't unsave your own meal plan.")
            elif request.user not in meal_plan.saved_by.all():
                messages.info(request, "You haven't saved this meal plan.")
            else:
                meal_plan.saved_by.remove(request.user)
                messages.success(request, "Meal plan unsaved.")
            return redirect("cookapp:mealplan_list")

        meal_plan_recipe_id = request.POST.get("meal_plan_recipe_id")
        scheduled_date = request.POST.get("scheduled_date")

        if not meal_plan_recipe_id or not scheduled_date:
            messages.error(request, "Invalid request. Please select a valid date.")
            return redirect("cookapp:mealplan_detail", mealplan_pk=meal_plan.pk)

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

        return redirect("cookapp:mealplan_detail", mealplan_pk=meal_plan.pk)

## Fix ##


class MealPlanListView(LoginRequiredMixin, ListView):
    model = MealPlan
    template_name = 'meal_plan/meal_plan_listview.html'
    context_object_name = 'mealplans'
    paginate_by = 6  

    def get_queryset(self):
        show_all = self.request.GET.get('show_all', False)

        if show_all:
            queryset = MealPlan.objects.all() 
        else:
            queryset = MealPlan.objects.filter(
                Q(status='public') | Q(user=self.request.user) | Q(saved_by=self.request.user)
            )

        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(name__icontains=query)

        return queryset.order_by('-start_date') 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['show_all'] = self.request.GET.get('show_all', False)
        return context


class UserMealPlanCreateView(CreateView):
    model = MealPlan
    form_class = MealPlanForm
    template_name = 'meal_plan/create_mealplan.html'
    success_url = reverse_lazy('cookapp:mealplan_list')

    def form_valid(self, form):

        if not form.cleaned_data.get('start_date'):
            form.instance.start_date = datetime.today().date()

        form.instance.user = self.request.user
        form.instance.image = self.request.FILES.get('image') 
        
        response = super().form_valid(form)
        return response

class MealPlanCreateView(CreateView):
    model = MealPlan
    #form_class = MealPlanForm
    template_name = "meal_plan/mealplan_form.html"
    fields = ["name", "start_date", "status", "visibility"]
    
    def form_valid(self, form):
        form.instance.user = self.request.user 
        #for user save stuff
        return super().form_valid(form)

##### HOME AND LOGIN #####

class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Community Pantry - Prep & Plate"
        return context
    
@method_decorator(login_not_required, name='dispatch')
class LoginView(FormView):
    template_name = 'registration/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('cookapp:home') 

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(self.request, username=username, password=password)
        if user is not None:
            login(self.request, user)
            return super().form_valid(form)
        else:
            form.add_error(None, "Invalid username or password")
            return self.form_invalid(form)
