from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')
    confirm_password = forms.CharField(widget=forms.PasswordInput, label='Повторите пароль')
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        help_texts = {
            'username': None,
            'email': None,
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        
        if password != confirm_password:
            raise forms.ValidationError("Пароли не совпадают")

class LoginForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль', error_messages={"required": "Напиши йоу"})
    class Meta:
        model = User
        fields = ['username', 'password']
        help_texts = {
            'username': None,
        }
        

    def clean(self):
        cleaned_data = super().clean()

        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise forms.ValidationError("Пизда")
        return cleaned_data
    