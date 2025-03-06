from django.urls import path
from .views import  (RecipeDetailView, ArticleListView, 
                    ArticleDetailView, ArticleUpdateView, 
                    ArticleDeleteView, ArticleCreateView, 
                    ArticleGalleryView
                    )

urlpatterns = [
    path('blog/articles',ArticleListView.as_view(), name='article_site'),
    path('blog/article/<int:pk>',ArticleDetailView.as_view(), name='article'),
    path('blog/article/<int:pk>/edit', ArticleUpdateView.as_view(), name='update'),
    path('blog/article/add', ArticleCreateView.as_view(), name='create'),
    path('blog/article/<int:pk>/delete', ArticleDeleteView.as_view(), name='delete'),
    path('blog/article/gallery', ArticleGalleryView.as_view(), name='gallery'),
    path('blog/recipe/<int:pk>/', RecipeDetailView.as_view(), name='recipe_detail'),
]
app_name = 'blog'
