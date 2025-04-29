from django import forms
from .models import CustomUser 
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm


class RegisterForm(forms.ModelForm):

    phone = forms.CharField(widget=forms.NumberInput, max_length=12, label='Номер')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')
    confirm_password = forms.CharField(widget=forms.PasswordInput, label='Повторите пароль')
    
    class Meta:
        model = CustomUser
        fields = ['phone', 'firstname', 'lastname', 'password']
        help_texts = {
            'phone': None,
        }
        labels = {
            'firstname': 'Имя',
            'lastname': 'Фамилия',
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        
        if password != confirm_password:
            raise forms.ValidationError("Пароли не совпадают")

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput, max_length=12, label='Номер')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')

    class Meta:
        model = CustomUser
        fields = ['phone', 'password']

    def clean(self):
       
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise forms.ValidationError("Номер или пароль неверны")
        return cleaned_data
    
    def get_user(self):
        return getattr(self, 'user', None)
    
