"""
URL configuration for skill_hat project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/v1/', include('api.urls')),
    
    # Frontend views
    path('', views.home, name='home'),
    path('search/', views.search_results, name='search_results'),
    
    # Authentication
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('register/customer/', views.customer_register_view, name='customer_register'),
    path('register/worker/', views.worker_register_view, name='worker_register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Worker profile (public view)
    path('worker/<int:worker_id>/', views.profile_view, name='profile'),
    
    # Dashboard views
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/update-profile/', views.update_profile_view, name='update_profile'),
    path('dashboard/update-worker/', views.update_worker_profile_view, name='update_worker'),
    path('dashboard/booking/<int:booking_id>/action/', views.booking_action_view, name='booking_action'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
