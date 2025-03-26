from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.apps import apps
from django.conf import settings
from datetime import datetime
from .models import Recipe, Ingredient, NutritionalInformation

@receiver(post_migrate)
def create_default_recipes(sender, **kwargs):
    if sender.name == apps.get_app_config('blog').name:  
        User = apps.get_model(settings.AUTH_USER_MODEL)  
        admin_user = User.objects.filter(is_superuser=True).first() 

        if admin_user:
            Recipe.objects.get_or_create(
                name="Classic Pancakes",
                description="Fluffy and delicious pancakes, perfect for breakfast.",
                preparation_time=10,
                cook_time=15,
                category="breakfast",
                difficulty="easy",
                servings=2,
                instructions="Mix ingredients, cook on a pan, and serve with syrup.",
                created_by=admin_user,
                created_on=datetime.now(),
                updated_on=datetime.now(),
                is_published=True,
                rating=4.5,
            )

            Recipe.objects.get_or_create(
                name="Spaghetti Bolognese",
                description="A rich and hearty Italian pasta dish.",
                preparation_time=15,
                cook_time=30,
                category="dinner",
                difficulty="medium",
                servings=4,
                instructions="Cook pasta, prepare sauce, and mix together.",
                created_by=admin_user,
                created_on=datetime.now(),
                updated_on=datetime.now(),
                is_published=True,
                rating=4.8,
            )

            Recipe.objects.get_or_create(
                name="Mango Smoothie",
                description="A refreshing mango smoothie with yogurt and honey.",
                preparation_time=5,
                cook_time=0,
                category="drink",
                difficulty="easy",
                servings=1,
                instructions="Blend mango, yogurt, and honey until smooth.",
                created_by=admin_user,
                created_on=datetime.now(),
                updated_on=datetime.now(),
                is_published=True,
                rating=4.7,
            )

                
            ingredients_data = [
                {"name": "Flour", "unit": "g", "estimated_expiration_date": "2025-12-31", "calories": 364, "proteins": 10, "fat": 1, "carbs": 76, "fiber": 2},
                {"name": "Tomato Sauce", "unit": "ml", "estimated_expiration_date": "2025-10-15", "calories": 40, "proteins": 1.5, "fat": 0.2, "carbs": 9, "fiber": 1},
                {"name": "Mango", "unit": "pcs", "estimated_expiration_date": "2025-07-20", "calories": 60, "proteins": 0.8, "fat": 0.4, "carbs": 15, "fiber": 1.6},
            ]

            for data in ingredients_data:
                ingredient, _ = Ingredient.objects.get_or_create(
                    name=data["name"],
                    defaults={"unit": data["unit"], "estimated_expiration_date": data["estimated_expiration_date"]}
                )

                NutritionalInformation.objects.update_or_create(
                    ingredient=ingredient,
                    defaults={
                        "calories": data["calories"],
                        "proteins": data["proteins"],
                        "fat": data["fat"],
                        "carbs": data["carbs"],
                        "fiber": data["fiber"],
                    }
                )

