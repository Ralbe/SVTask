from django.shortcuts import render
from django.http import HttpRequest
from . import models as mo
# from .forms import UserRegistrationForm

def index(request: HttpRequest):
    return render(request, 'main/main.html', {'user': request.user})

def vacations(request: HttpRequest):
    vac_all = mo.Vacation.objects.all()
    return render(request, 'main/vacations.html', {'vacs': vac_all})

def advertisements(request: HttpRequest):
    ads_all = mo.Advertisement.objects.all()
    return render(request, 'main/advertisements.html', {'ads': ads_all})

