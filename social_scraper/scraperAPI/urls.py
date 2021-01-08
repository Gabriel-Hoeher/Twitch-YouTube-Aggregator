from django.urls import path
from . import views

urlpatterns = [
    path('', views.baseMedia, name='media'),
    path('creators/', views.viewCreators, name='creators'),
]