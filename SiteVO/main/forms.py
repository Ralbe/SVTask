from django import forms
from .models import Vacation, Advertisement

class CreateVacForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput, max_length=128, label='Название вакансии')
    description = forms.CharField(widget=forms.Textarea, max_length=1024, label='Описание вакансии')
    salary = forms.IntegerField(widget=forms.NumberInput({"min": 1, "value": 1000}), label='Заработная плата')
    
    class Meta:
        model = Vacation
        fields = ['title', 'description', 'salary']
 
class CreateAdForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput, max_length=128, label='Название объявления')
    description = forms.CharField(widget=forms.Textarea, max_length=1024, label='Описание объявления')
    price = forms.IntegerField(widget=forms.NumberInput({"min": 1, "value": 1000}), label='Стоимость')
    
    class Meta:
        model = Advertisement
        fields = ['title', 'description', 'price']
 