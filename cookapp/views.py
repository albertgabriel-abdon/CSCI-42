from django.shortcuts import render, get_object_or_404, redirect

from datetime import datetime

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

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
                    CreateRecipeForm
                    )

from django.db.models import Q
from .models import (Recipe, MealPlan,
                     InventoryManager, Ingredient, 
                     NutritionalInformation, GroceryList,
                    UserRequest, MealPlanRecipe
                    )

from django.views import View


##### RECIPE #####

class RecipeCreateView(LoginRequiredMixin, View):
    form_class = CreateRecipeForm
    
    def get(self, request, mealplan_pk=None):
        form = self.form_class()  # Initialize an empty form
        return render(request, 'recipe/create_recipe.html', {
            'form': form,  # Pass form to template
            'category_choices': Recipe.CATEGORY_CHOICES,
            'difficulty_choices': Recipe.DIFFICULTY_CHOICES,
            'mealplan_pk': mealplan_pk
        })

    def post(self, request, mealplan_pk=None):
        form = self.form_class(request.POST)
        if form.is_valid():
            # Save the new recipe
            recipe = form.save(commit=False)
            recipe.created_by = request.user
            recipe.save()
            
            messages.success(request, "Recipe created successfully!")

            if mealplan_pk:
                return redirect("cookapp:mealplan_detail", mealplan_pk=mealplan_pk)

            return redirect(recipe.get_absolute_url())
        else:
            # If the form is invalid, return to the form with errors
            messages.error(request, "All fields are required.")
            return render(request, 'recipe/create_recipe.html', {
                'form': form,  # Re-render the form with errors
                'category_choices': Recipe.CATEGORY_CHOICES,
                'difficulty_choices': Recipe.DIFFICULTY_CHOICES,
                'mealplan_pk': mealplan_pk
            })
    
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

    def get_queryset(self):
        query = self.request.GET.get('q')
        user = self.request.user

        queryset = MealPlan.objects.filter(
            Q(visibility='public') | Q(user=user)
        )
        
        if query:
            queryset = queryset.filter(name__icontains=query)
        
        return queryset.order_by('-start_date')

class UserMealPlanCreateView(CreateView):
    model = MealPlan
    form_class = MealPlanForm
    template_name = 'meal_plan/create_mealplan.html'
    success_url = reverse_lazy('cookapp:mealplan_list') 

    def form_valid(self, form):
        if not form.cleaned_data.get('start_date'):
            form.instance.start_date = datetime.today().date()
        
        form.instance.user = self.request.user
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