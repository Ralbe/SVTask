from django import forms
from .models import Vacation, Advertisement

class MyModelForm(forms.ModelForm):
    error_css_class = 'class-error'
    required_css_class = 'form-group'
    

class CreateVacForm(MyModelForm):
    title = forms.CharField(widget=forms.TextInput({'placeholder': "Введите название"}), max_length=128, label='Название вакансии')
    description = forms.CharField(widget=forms.Textarea({'placeholder': "Подробно опишите, что вы предлагаете", 'style': 'resize:none'}), max_length=1024, label='Описание вакансии')
    salary = forms.IntegerField(widget=forms.NumberInput({"min": 1}), label='Заработная плата')
    
    class Meta:
        model = Vacation
        fields = ['title', 'description', 'salary']

 
class CreateAdForm(MyModelForm):
    title = forms.CharField(widget=forms.TextInput({'placeholder': "Введите название"}), max_length=128, label='Название объявления')
    description = forms.CharField(widget=forms.Textarea({'placeholder': "Подробно опишите, что вы предлагаете", 'style': 'resize:none'}), max_length=1024, label='Описание объявления')
    price = forms.IntegerField(widget=forms.NumberInput({"min": 1}), label='Стоимость')
    
    class Meta:
        model = Advertisement
        fields = ['title', 'description', 'price']
 