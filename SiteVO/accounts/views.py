import sys
sys.path.append("..")
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from .forms import RegisterForm, LoginForm
from main.models import Vacation, Advertisement, FavoriteAdvertisement, FavoriteVacation
# Create your views here.

def register_view(request: HttpRequest):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request: HttpRequest):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
            return redirect('profile')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def profile_view(request: HttpRequest):
    cnt = [
        Vacation.objects.filter(user_id=request.user.id).count(),
        FavoriteVacation.objects.filter(user_id=request.user.id).count(),
        FavoriteAdvertisement.objects.filter(user_id=request.user.id).count(),
        Advertisement.objects.filter(user_id=request.user.id).count()
    ]
    return render(request, "accounts/profile.html", {'user': request.user, 'count': cnt})

def logout_view(request: HttpRequest):
    logout(request)
    return redirect('login')

