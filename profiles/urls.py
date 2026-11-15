from django.urls import path

from . import views

urlpatterns = [
    path('discover/', views.discover, name='discover'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
]