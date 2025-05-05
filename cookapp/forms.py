from django import forms  
from .models import Recipe, MealPlan, Ingredient, InventoryManager, GroceryList
    
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
        fields = ['name', 'description', 'special_tags', 'start_date', 'status', 'visibility', 'image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['start_date'].required = False

class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ["name", "estimated_expiration_date", "unit"]

    def __init__(self, *args, **kwargs):
        super(IngredientForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class InventoryEditForm(forms.ModelForm):
    class Meta:
        model = InventoryManager
        fields = ["quantity", "is_buyer"]

class EditMealPlanForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter meal plan name',
            'required': 'required'
        })
    )

    start_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'required': 'required'
        })
    )

    status = forms.ChoiceField(
        choices=MealPlan.STATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    visibility = forms.ChoiceField(
        choices=MealPlan.VISIBILITY_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    image = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control-file'
        })
    )

    class Meta:
        model = MealPlan
        fields = ['name', 'start_date', 'status', 'visibility', 'image']

class CreateRecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = [
            'name', 
            'category', 
            'difficulty', 
            'preparation_time', 
            'cook_time', 
            'servings', 
            'description', 
            'instructions',
            'image'  
            
        ]
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter recipe name'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'difficulty': forms.Select(attrs={'class': 'form-select'}),
            'preparation_time': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter preparation time in minutes'}),
            'cook_time': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter cook time in minutes'}),
            'servings': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter servings'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter description'}),
            'instructions': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter instructions'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}) 
        }

class GroceryListForm(forms.ModelForm):
    class Meta:
        model = GroceryList
        fields = ['ingredient', 'quantity', 'status']


