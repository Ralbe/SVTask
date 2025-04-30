from django.db import models

# Create your models here.

class Vacation(models.Model):
    ad_id = models.AutoField(primary_key=True)
    user_id = models.BigIntegerField()
    title = models.CharField("Название вакансии", max_length=128)
    description = models.TextField("Описание")
    salary = models.IntegerField('Заработная плата')
    count_views = models.BigIntegerField("Просмотры", default=0)

    class Meta:
        ordering = ['ad_id']

class Advertisement(models.Model):
    ad_id = models.AutoField(primary_key=True)
    user_id = models.BigIntegerField()
    title = models.CharField("Название объявления", max_length=128)
    description = models.TextField("Описание")
    price = models.IntegerField('Стоимость')
    count_views = models.BigIntegerField("Просмотры", default=0)

    class Meta:
        ordering = ['ad_id']

class FavoriteVacation(models.Model):
    ad_id = models.BigIntegerField()
    user_id = models.BigIntegerField()

    class Meta:
        ordering = ['ad_id']

class FavoriteAdvertisement(models.Model):
    ad_id = models.BigIntegerField()
    user_id = models.BigIntegerField()

    class Meta:
        ordering = ['ad_id']