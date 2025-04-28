from django.db import models

# Create your models here.

class Vacation(models.Model):
    ad_id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    title = models.CharField("Название вакансии", max_length=128)
    description = models.TextField("Описание")

class Advertisement(models.Model):
    ad_id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    title = models.CharField("Название объявления", max_length=128)
    description = models.TextField("Описание")