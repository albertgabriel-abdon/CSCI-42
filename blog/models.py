from django.db import models
from django.urls import reverse
from django.conf import settings
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.apps import apps
  
class ArticleCategory(models.Model):
   name = models.CharField(max_length=255, null=True)
   description = models.TextField()
   
   class Meta:
        ordering = ['name']
        
   def __str__(self):
     return '{}'.format(self.name)

@receiver(post_migrate)  
def create_article_categories(sender, **kwargs):
    if sender.name == apps.get_app_config('blog').name:
        ArticleCategory.objects.get_or_create(name='Controversial', description='Controversial articles')
        ArticleCategory.objects.get_or_create(name='Personal', description='Personal articles')
        ArticleCategory.objects.get_or_create(name='Creative', description='Creative articles')
  
class Article(models.Model):
   title = models.CharField(max_length=255, null=True)
   author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
    )
   entry = models.TextField()
   category = models.ForeignKey(
      ArticleCategory,
      on_delete=models.SET_NULL,
      null=True,
      related_name = "article",
   )  
   header_image = models.ImageField(upload_to='images/',null=True)
   created_on = models.DateTimeField(auto_now_add=True, null=True)
   updated_on = models.DateTimeField(auto_now=True, null=True)
   
   class Meta:
        ordering = ['-created_on']

   def __str__(self):
      return '{}'.format(self.title, self.entry)
      
   def get_absolute_url(self):
      return reverse('blog:article', args=[str(self.pk)])
   
   def get_create_url(self):
      return reverse('blog:create', args=[str(self.pk)])
   
   def get_update_url(self):
      return reverse('blog:update', args=[str(self.pk)])
   
   def get_delete_url(self):
      return reverse('blog:delete', args=[str(self.pk)])

class Comment(models.Model):
   author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
    )
   article = models.ForeignKey(
      Article,
      on_delete=models.SET_NULL,
      null=True,
      related_name = "comment",
   )  
   entry = models.TextField()
   created_on = models.DateTimeField(auto_now_add=True, null=True)
   updated_on = models.DateTimeField(auto_now=True, null=True)
   
   class Meta:
        ordering = ['created_on']

   
   
# Create your models here.
