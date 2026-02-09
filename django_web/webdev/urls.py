"""
URL configuration for webdev project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    
    path('play/<int:story_id>/', views.play_game, name='play_game'),
    path('play/<int:story_id>/<int:page_id>/', views.play_game, name='play_step'),
    
  
    # This fixes the "NoReverseMatch" error for your blue button
    path('story/<int:story_id>/map/', views.story_map, name='story_map'),
    
    # These handle the rating and report submissions
    path('rate/<int:story_id>/', views.submit_rating, name='submit_rating'),
    path('report/<int:story_id>/', views.report_story, name='report_story'),

    # --- AUTHENTICATION ---
    path('register/', views.register, name='register'),
    path('accounts/', include('django.contrib.auth.urls')),

    path('story/<int:story_id>/reviews/', views.story_reviews, name='story_reviews'),
]