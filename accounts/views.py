from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView

from accounts.forms import SignUpForm


class SignUpView(CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy("home")
    template_name = "registration/sign_up.html"

#from .forms import SignUpForm

#def signup(request):
    #if request.method == 'POST':
        #form = SignUpForm(request.POST)
       # if form.is_valid():
           # user = form.save()
           # login(request, user)
           # return redirect('article_site.html')
 #   else:
     #   form = SignUpForm()
  #  return render(request, 'sign_up.html', {'form': form})

 
# Create your views here.
