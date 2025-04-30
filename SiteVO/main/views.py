from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest
from django.contrib.auth.decorators import login_required
from django.db.models import QuerySet
from .forms import CreateVacForm, CreateAdForm
from . import models as mo
from accounts.models import CustomUser
# from .forms import UserRegistrationForm

def index(request: HttpRequest):
    return render(request, 'main/main.html', {'user': request.user})

def vacations(request: HttpRequest):
    title = request.GET.get('title')
    salary = request.GET.get('salary')
    
    if not salary:
        salary = 0
    
    if not title:
        title = ''

    vac_all = mo.Vacation.objects.all()
    vac_all = [vac for vac in vac_all if title in vac.title and vac.salary >= int(salary)]

    return render(request, 'main/vacations.html', {'vacs': vac_all})

def advertisements(request: HttpRequest):
    title = request.GET.get('title')
    price = request.GET.get('price')
    
    if not price:
        price = 0
    
    if not title:
        title = ''

    ads_all = mo.Advertisement.objects.all()
    ads_all = [ads for ads in ads_all if title in ads.title and ads.price >= int(price)]

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

@login_required
def vacation_view(request: HttpRequest):
    ad_id = request.GET.get('id')
    add_user_id = request.GET.get('add_favorite_user')
    delete_user_id = request.GET.get('delete_favorite_user')
    delete_id = request.GET.get('delete')

    if delete_id and int(delete_id) == request.user.id:
        vac = mo.Vacation.objects.filter(ad_id=ad_id, user_id=request.user.id)
        favvacs = mo.FavoriteVacation.objects.filter(ad_id=ad_id)
        for favvac in favvacs:
            favvac.delete()
        vac.delete()
        return redirect('vacations')

    if add_user_id and int(add_user_id) != request.user.id: 
        add_user_id = None
    
    if delete_user_id and int(delete_user_id) != request.user.id: 
        delete_user_id = None


    favorite = False
    favvac = mo.FavoriteVacation.objects.filter(ad_id=ad_id, user_id=request.user.id)
    if favvac:
        favorite = True
        if delete_user_id:
            favvac.delete()
            favorite = False
    elif add_user_id:
        mo.FavoriteVacation.objects.create(ad_id=ad_id, user_id=add_user_id)
        favorite = True
    
    vac = mo.Vacation.objects.get(ad_id=ad_id)
    user_id = vac.user_id

    user = CustomUser.objects.get(id=user_id)
    count_fav = mo.FavoriteVacation.objects.filter(ad_id=ad_id).count()
    
    if int(user_id) != request.user.id and not favorite:
        vac.count_views += 1
        vac.save()
    return render(request, 'main/vacation.html', {'vac': vac, 'create_user': user, 'favorite': favorite, 'count_fav': count_fav})

@login_required
def advertisement_view(request: HttpRequest):
    ad_id = request.GET.get('id')
    add_user_id = request.GET.get('add_favorite_user')
    delete_user_id = request.GET.get('delete_favorite_user')
    delete_id = request.GET.get('delete')

    if delete_id and int(delete_id) == request.user.id:
        ad = mo.Advertisement.objects.filter(ad_id=ad_id, user_id=request.user.id)
        favads = mo.FavoriteAdvertisement.objects.filter(ad_id=ad_id)
        for favad in favads:
            favad.delete()
        ad.delete()
        return redirect('advertisements')

    if add_user_id and int(add_user_id) != request.user.id: 
        add_user_id = None
    
    if delete_user_id and int(delete_user_id) != request.user.id: 
        delete_user_id = None

    favorite = False
    favvac = mo.FavoriteAdvertisement.objects.filter(ad_id=ad_id, user_id=request.user.id)
    if favvac:
        favorite = True
        if delete_user_id:
            favvac.delete()
            favorite = False
    elif add_user_id:
        mo.FavoriteAdvertisement.objects.create(ad_id=ad_id, user_id=add_user_id)
        favorite = True
    
    
    ad = mo.Advertisement.objects.get(ad_id=ad_id)
    user_id = ad.user_id
    user = CustomUser.objects.get(id=user_id)
    return render(request, 'main/advertisement.html', {'ad': ad, 'create_user': user, 'favorite': favorite})

@login_required
def favorite_vacs_view(request: HttpRequest):
    favvacs = mo.FavoriteVacation.objects.filter(user_id=request.user.id)
    
    favvacid = [vac.ad_id for vac in favvacs]

    vacs = [vac for vac in mo.Vacation.objects.all() if vac.ad_id in favvacid]

    return render(request, 'main/favorite.html', {'ads': vacs, 'vacs': True, 'fav': True})

@login_required
def favorite_ads_view(request: HttpRequest):
    favads = mo.FavoriteAdvertisement.objects.filter(user_id=request.user.id)
    
    favadsid = [ad.ad_id for ad in favads]
    
    ads = [ad for ad in mo.Advertisement.objects.all() if ad.ad_id in favadsid]
    
    return render(request, 'main/favorite.html', {'ads': ads, 'vacs': False, 'fav': True})

@login_required
def my_ads_view(request: HttpRequest):
    ads = mo.Advertisement.objects.filter(user_id=request.user.id)
    return render(request, 'main/favorite.html', {'ads': ads, 'vacs': False, 'fav': False})


@login_required
def my_vacs_view(request: HttpRequest):
    vacs = mo.Vacation.objects.filter(user_id=request.user.id)
    return render(request, 'main/favorite.html', {'ads': vacs, 'vacs': True, 'fav': False})


