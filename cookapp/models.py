from django.db import models
from django.urls import reverse
from django.conf import settings
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.apps import apps
from django.utils.timezone import now
from django.utils.timesince import timesince
  

class MealPlan(models.Model):
   
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    
    VISIBILITY_CHOICES = [
        ('private', 'Private'),
        ('friends', 'Friends-Only'),
        ('public', 'Public'),
    ]

    special_tags = models.CharField(
        max_length=100,
        choices=[
            ('vegetarian', 'Vegetarian'),
            ('vegan', 'Vegan'),
            ('gluten_free', 'Gluten-Free'),
            ('keto', 'Keto'),
            ('none', 'None'),
        ],
        default='none' 
    )

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    start_date = models.DateField(default=now)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='active'
    )
    visibility = models.CharField(
        max_length=10,
        choices=VISIBILITY_CHOICES,
        default='private'
    )

    image = models.ImageField(upload_to='mealplans/', blank=True, null=True)
    breakfast = models.CharField(max_length=255, blank=True, null=True)
    lunch = models.CharField(max_length=255, blank=True, null=True)
    dinner = models.CharField(max_length=255, blank=True, null=True)
    saved_by = models.ManyToManyField(
    settings.AUTH_USER_MODEL,
    related_name='saved_mealplans',
    blank=True
)

    class Meta:
        ordering = ['-start_date']

    def save(self, *args, **kwargs):
        self.status = self.status.lower()
        self.visibility = self.visibility.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.get_status_display()}"

    def get_absolute_url(self):
        return reverse('cookapp:mealplan_detail', args=[str(self.pk)])

    def get_update_url(self):
        return reverse('cookapp:mealplan_update', args=[str(self.pk)])

    def get_delete_url(self):
        return reverse('cookapp:mealplan_delete', args=[str(self.pk)])

class MealPlanRecipe(models.Model):
    meal_plan = models.ForeignKey(
        'MealPlan', 
        on_delete=models.CASCADE, 
        related_name='meal_recipes'
    )
    recipe = models.ForeignKey(
        'Recipe', 
        on_delete=models.CASCADE, 
        related_name='meal_plans'
    )
    scheduled_date = models.DateField()

    class Meta:
        ordering = ['scheduled_date']
        unique_together = ('meal_plan', 'recipe', 'scheduled_date')  

    def __str__(self):
        return f"{self.recipe.name} in {self.meal_plan.name} on {self.scheduled_date}"


class Recipe(models.Model):
    CATEGORY_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('snacks', 'Snacks'),
        ('desserts', 'Desserts'),
        ('dinner', 'Dinner'),
        ('drink', 'Drink'),
        ('soup', 'Soup'),
        ('salad', 'Salad'),
    ]

    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField()
    preparation_time = models.PositiveIntegerField(help_text="Time in minutes")
    cook_time = models.PositiveIntegerField(help_text="Time in minutes")
    category = models.CharField(
        max_length=10,
        choices=CATEGORY_CHOICES,
        default='lunch'
    )
    difficulty = models.CharField(
        max_length=10,
        choices=DIFFICULTY_CHOICES,
        default='medium'
    )
    servings = models.PositiveIntegerField()
    instructions = models.TextField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)
    image = models.ImageField(upload_to='recipe_images/', null=True, blank=True) 
    rating = models.FloatField(default=0.0)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return f"{self.name} - {self.get_category_display()}"

    def get_absolute_url(self):
        return reverse('cookapp:recipe_detail', args=[str(self.pk)])

    def get_update_url(self):
        return reverse('cookapp:recipe_update', args=[str(self.pk)])

    def get_delete_url(self):
        return reverse('cookapp:recipe_delete', args=[str(self.pk)])

    def set_rating(self, new_rating):
        """Set the rating for the recipe."""
        self.rating = round(new_rating, 1)
        self.save()

class MealPlanRecipe(models.Model):
    meal_plan = models.ForeignKey(
        'MealPlan', 
        on_delete=models.CASCADE, 
        related_name='meal_recipes'
    )
    recipe = models.ForeignKey(
        'Recipe', 
        on_delete=models.CASCADE, 
        related_name='meal_plans'
    )
    scheduled_date = models.DateField()

    class Meta:
        ordering = ['scheduled_date']
        unique_together = ('meal_plan', 'recipe', 'scheduled_date')  

    def __str__(self):
        return f"{self.recipe.name} in {self.meal_plan.name} on {self.scheduled_date}"

class NutritionalInformation(models.Model):
    ingredient = models.OneToOneField(
        'Ingredient', 
        on_delete=models.CASCADE, 
        related_name='nutrition'
    )
    calories = models.FloatField()
    proteins = models.FloatField()
    fat = models.FloatField()
    carbs = models.FloatField()
    fiber = models.FloatField()

    def __str__(self):
        return f"Nutrition for {self.ingredient.name}"  

class Ingredient(models.Model):
    name = models.CharField(max_length=255, unique=True)
    estimated_expiration_date = models.DateField()
    unit = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('cookapp:ingredient_detail', args=[str(self.pk)]) 

    def get_update_url(self):
        return reverse('cookapp:ingredient_update', args=[str(self.pk)]) 

    def get_delete_url(self):
        return reverse('cookapp:ingredient_delete', args=[str(self.pk)])  
    
    def nutrition(self):
        return getattr(self, 'nutrition', None)

class UserRequest(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
    )
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    distance = models.IntegerField() 
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} requests {self.quantity} {self.ingredient.name}"
    
    def time_ago(self):
        return timesince(self.updated_on, now()) + " ago"

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        'Recipe', 
        on_delete=models.CASCADE, 
        related_name='recipe_ingredients'
    )
    ingredient = models.ForeignKey(
        'Ingredient', 
        on_delete=models.CASCADE, 
        related_name='recipe_ingredients'
    )
    quantity = models.FloatField()

    def __str__(self):
        return f"{self.quantity} {self.ingredient.unit} of {self.ingredient.name} in {self.recipe.name}"

class InventoryManager(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)  
    is_buyer = models.BooleanField(default=False)  

    class Meta:
        unique_together = ('user', 'ingredient') 

    def __str__(self):
        return f"{self.user.username}'s {self.ingredient.name} ({self.quantity})"

    def get_absolute_url(self):
        return reverse('cookapp:inventory_detail', args=[str(self.pk)]) 

    def get_update_url(self):
        return reverse('cookapp:inventory_edit', args=[str(self.pk)]) 

    def get_delete_url(self):
        return reverse('cookapp:inventory_delete', args=[str(self.pk)]) 
    
class GroceryList(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('sold_out', 'Sold Out'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="grocery_lists"
    )
    ingredient = models.ForeignKey(
        'Ingredient', 
        on_delete=models.CASCADE, 
        related_name="grocery_items"
    )
    quantity = models.PositiveIntegerField(default=1)  
    updated_on = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='available'
    )

    class Meta:
        ordering = ['-updated_on']
        unique_together = ('user', 'ingredient')  

    def __str__(self):
        return f"{self.ingredient.name} ({self.get_status_display()}) - {self.user.username}"

    def get_absolute_url(self):
        return reverse('cookapp:grocery_list_detail', args=[str(self.pk)])  

    def get_update_url(self):
        return reverse('cookapp:grocery_list_update', args=[str(self.pk)])  

    def get_delete_url(self):
        return reverse('cookapp:grocery_list_delete', args=[str(self.pk)]) 
