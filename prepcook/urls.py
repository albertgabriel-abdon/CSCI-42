"""
URL configuration for prepcook project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import TemplateView
from accounts.views import SignUpView
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_not_required
from cookapp.views import DirectPasswordResetView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('cookapp.urls', namespace = 'cookapp')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', login_not_required(SignUpView.as_view()), name="sign_up"), 
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    
    # Password reset URLs
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
    # Direct password reset URL
    path('direct_password_reset/', DirectPasswordResetView.as_view(), name='direct_password_reset'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
