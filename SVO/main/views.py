from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest
from . import models as mo
# from .forms import UserRegistrationForm

def index(request: HttpRequest):
    return render(request, 'main/main.html')


def about(request: HttpRequest):
    return HttpResponse("<h3>About</h3>")

def vacations(request: HttpRequest):
    vac_all = mo.Vacation.objects.all()
    return render(request, 'main/vacations.html', {'vacs': vac_all})

# def register(request: HttpRequest):
#     print(request.method)
#     if request.method == "POST":
#         user_form = UserRegistrationForm(request.POST)
#         if user_form.is_valid():
#             new_user = user_form.save()
#             new_user.set_password(user_form.cleaned_data['password'])
            
#             new_user.save()
#             return redirect("/vacations")
#     else:
#         user_form = UserRegistrationForm()
#     return render(request, 'main/register.html', {'user_form': user_form})

def advertisements(request: HttpRequest):
    ads_all = mo.Advertisement.objects.all()
    return render(request, 'main/advertisements.html', {'ads': ads_all})