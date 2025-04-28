from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('vacations', views.vacations,  name='vacations'),
    path('advertisements', views.advertisements,  name='advertisements'),
]