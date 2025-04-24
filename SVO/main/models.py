from django.db import models

# Create your models here.

class User(models.Model):
    id = models.AutoField(primary_key=True)
    firstname = models.CharField("Имя", max_length=64)
    lastname = models.CharField("Фамилия", max_length=64)
    email = models.EmailField("Почта")
    password = models.CharField("Пароль", max_length=128)

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