from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Vacation)
admin.site.register(models.Advertisement)
admin.site.register(models.FavoriteVacation)
admin.site.register(models.FavoriteAdvertisement)
