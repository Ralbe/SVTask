from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.contrib.auth.decorators import login_required
from .forms import CreateVacForm, CreateAdForm
from . import models as mo
from accounts.models import CustomUser
# from .forms import UserRegistrationForm

def index(request: HttpRequest):
    return render(request, 'main/main.html', {'user': request.user})

def vacations(request: HttpRequest):
    vac_all = mo.Vacation.objects.all()
    return render(request, 'main/vacations.html', {'vacs': vac_all})

def advertisements(request: HttpRequest):
    ads_all = mo.Advertisement.objects.all()
    return render(request, 'main/advertisements.html', {'ads': ads_all})

@login_required
def create_vac(request: HttpRequest):
    if request.method == 'POST':
        form = CreateVacForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user_id = request.user.id
            form.save()
            return redirect('vacations')
    else:
        form = CreateVacForm()

    return render(request, 'main/create_vac.html', {'user': request.user, 'form': form})

@login_required
def create_ad(request: HttpRequest):
    if request.method == 'POST':
        form = CreateAdForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user_id = request.user.id
            form.save()
            return redirect('advertisements')
    else:
        form = CreateAdForm()

    return render(request, 'main/create_ad.html', {'user': request.user, 'form': form})


def vacation_view(request: HttpRequest):
    ad_id = request.GET.get('id')
    vac = mo.Vacation.objects.get(ad_id=ad_id)
    user_id = vac.user_id
    user = CustomUser.objects.get(id=user_id)
    return render(request, 'main/vacation.html', {'vac': vac, 'user': user})


def advertisement_view(request: HttpRequest):
    ad_id = request.GET.get('id')
    ad = mo.Advertisement.objects.get(ad_id=ad_id)
    user_id = ad.user_id
    user = CustomUser.objects.get(id=user_id)
    return render(request, 'main/advertisement.html', {'ad': ad, 'user': user})