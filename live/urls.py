from django.urls import path

from . import views

urlpatterns = [
    path('', views.lobby, name='live_lobby'),
    path('new/', views.create_room, name='live_create'),
    path('call/<int:user_id>/', views.private_call, name='private_call'),
    path('call/<int:user_id>/token/', views.private_call_token, name='private_call_token'),
    path('r/<str:slug>/', views.room, name='live_room'),
    path('r/<str:slug>/token/', views.room_token, name='live_room_token'),
    path('r/<str:slug>/end/', views.end_room, name='live_room_end'),
]