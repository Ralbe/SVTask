from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('vacations', views.vacations,  name='vacations'),
    path('advertisements', views.advertisements,  name='advertisements'),
    path('create_vac', views.create_vac,  name='create_vac'),
    path('create_ad', views.create_ad,  name='create_ad'),
    path('vacation', views.vacation_view, name='vacation'),
    path('advertisement', views.advertisement_view, name='advertisement'),
    path('favorite_vacs', views.favorite_vacs_view, name='favorite_vacs'),
    path('favorite_ads', views.favorite_ads_view, name='favorite_ads'),
    path('my_vacs', views.my_vacs_view, name='my_vacs'),
    path('my_ads', views.my_ads_view, name='my_ads'),
]