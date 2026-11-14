from django.urls import path

from . import views

urlpatterns = [
    path('', views.match_list, name='match_list'),
    path('swipe/<int:user_id>/', views.swipe, name='swipe'),
    path('block/<int:user_id>/', views.block_user, name='block_user'),
    path('report/<int:user_id>/', views.report_user, name='report_user'),
]