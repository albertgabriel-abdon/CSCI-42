from django.utils.timezone import now
from datetime import date, timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from django.db import IntegrityError
from django.views.generic import TemplateView
from datetime import datetime

from django.views.generic.edit import FormView
from django.views.generic import DeleteView, CreateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import (Article, ArticleCategory, 
                     Comment, Recipe, MealPlan,
                     )
from .forms import ArticleForm, CommentForm, RecipeForm, RecipeAddForm

from django.shortcuts import get_object_or_404, redirect
from django.views import View

from .models import MealPlan, Recipe, MealPlanRecipe

class RecipeAddView(View):
    def get(self, request, pk):
        meal_plan = get_object_or_404(MealPlan, pk=pk, user=request.user)
        recipes = Recipe.objects.all()  
        default_date = (now() + timedelta(days=30)).date() 

        return render(request, 'blog/recipe_add_form.html', {
            'meal_plan': meal_plan,
            'recipes': recipes,
            'default_date': default_date,
        })

    def post(self, request, pk):
        meal_plan = get_object_or_404(MealPlan, pk=pk, user=request.user)
        recipe_id = request.POST.get("recipe_id")
        scheduled_date = request.POST.get("scheduled_date")

        if not recipe_id:
            messages.error(request, "Recipe ID is required.")
            return redirect("blog:mealplan_detail", pk=meal_plan.pk)

        recipe = get_object_or_404(Recipe, pk=recipe_id)

        if not scheduled_date:
            scheduled_date = (now() + timedelta(days=30)).date()
        else:
            scheduled_date = datetime.strptime(scheduled_date, "%Y-%m-%d").date() 

        MealPlanRecipe.objects.create(
            meal_plan=meal_plan,
            recipe=recipe,
            scheduled_date=scheduled_date
        )

        messages.success(request, "Recipe added to meal plan successfully!")
        return redirect("blog:mealplan_detail", pk=meal_plan.pk)

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recipes"] = Recipe.objects.all()  
        return context

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

class MealPlanDeleteView(DeleteView):
    model = MealPlan
    template_name = "mealplan_confirm_delete.html"
    success_url = reverse_lazy("blog:mealplan_list")
   

class RecipeDetailView(DetailView):
    model = Recipe
    template_name = "recipe_detail.html"  
    context_object_name = 'recipe'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_authenticated:
            meal_plans = MealPlan.objects.filter(user=user)
            meal_plan_recipes = MealPlanRecipe.objects.filter(recipe=self.object, meal_plan__user=user)
        else:
            meal_plans = MealPlan.objects.none()
            meal_plan_recipes = MealPlanRecipe.objects.none() 

        default_scheduled_date = date.today() + timedelta(days=30)

        context["meal_plans"] = meal_plans
        context["meal_plan_recipes"] = meal_plan_recipes
        context["default_scheduled_date"] = default_scheduled_date

        return context
    #context_obj_name is relevant
    #context['recipes'] = Recipe.objects.all()
    # #context['recipes'] = Recipe.objects.filter(is_published=True) for site itself

class RecipeCreateView(LoginRequiredMixin, CreateView):
    model = Recipe
    form_class = RecipeForm
    template_name = "recipe_form.html"

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

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
         
