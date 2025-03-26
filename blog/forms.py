from django import forms  
from .models import Article, Comment, Recipe, MealPlan, Ingredient, InventoryManager
    
class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        exclude = ['author']
        fields = '__all__'
        labels = {
            'title': 'Article name',
            'entry': '',
        }
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Write your entry title...'}),
            'entry': forms.Textarea(attrs={
                'placeholder': 'Write your entry here...',
                'style': 'white-space: pre-wrap; overflow-wrap: break-word;',
                }),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = 'Choose category:'
        

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['entry']
        labels = {
            'entry': '',
        }
        
        widgets = { 
                'entry': forms.Textarea(attrs={
                'placeholder': 'Write your entry here...',
                }),
         }
        
class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['name', 'description', 'preparation_time', 'cook_time', 'category', 'difficulty', 'servings', 'instructions', 'is_published']

class RecipeAddForm(forms.Form):
    recipe = forms.ModelChoiceField(
        queryset=Recipe.objects.all(),
        empty_label="Select a Recipe",
        required=True
    )
    scheduled_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}),
        required=True
    )

class MealPlanForm(forms.ModelForm):
    class Meta:
        model = MealPlan
        fields = ['name', 'start_date', 'status', 'visibility']

class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ["name", "estimated_expiration_date", "unit"]

class InventoryEditForm(forms.ModelForm):
    class Meta:
        model = InventoryManager
        fields = ["quantity", "is_buyer"]
