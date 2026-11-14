from django.urls import path

from . import views

urlpatterns = [
    path('<int:user_id>/', views.thread, name='chat_thread'),
    path('<int:user_id>/send/', views.send, name='chat_send'),
    path('<int:user_id>/poll/', views.poll, name='chat_poll'),
]