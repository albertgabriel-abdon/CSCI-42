from django.views.generic import DeleteView, CreateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy

from .models import Article, ArticleCategory, Comment
from .forms import ArticleForm, CommentForm
    
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
         
class ArticleDetailView(DetailView):
    model = Article
    template_name = 'article.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_main'] = False  
        context['comment'] = Comment.objects.all()
        context['form'] = CommentForm()
        return context
    
    def post(self, request, *args, **kwargs):
        comments = Comment()
        comments.author = request.user
        comments.entry = request.POST.get('entry')
        comments.article = self.get_object()
        comments.save()
        
        return self.get(request, *args, **kwargs)
    
class ArticleCreateView(CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'article_create.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_category'] = int(self.request.GET.get('category', 0))
        context['is_main'] = False
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

class ArticleUpdateView(UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'article_edit.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_main'] = False  
        return context
    
class ArticleDeleteView(DeleteView):
    model = Article
    def get_success_url(self):
        return reverse_lazy('blog:article_site')
    
class ArticleGalleryView(ListView):
    model = Article
    form_class = ArticleForm
    template_name = 'article_gallery.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_main'] = False  
        context['articles'] = Article.objects.all()
        return context
    
# Create your views here.
