from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('about-us', views.about),
    path('vacations', views.vacations),
    #path('register', views.register),
    path('advertisements', views.advertisements),
]