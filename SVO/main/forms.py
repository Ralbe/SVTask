from django.contrib.auth.models import User
from django.forms import ModelForm, CharField, PasswordInput, ValidationError

# class UserRegistrationForm(ModelForm):
#     password = CharField(label='Пароль', widget=PasswordInput)
#     password2 = CharField(label='Повторите пароль', widget=PasswordInput)

#     class Meta:
#         model = User
#         fields = ("firstname", 'lastname', 'email')

#     def clean_password2(self):
#         cd = self.cleaned_data
#         if cd['password'] != cd['password2']:
#             raise ValidationError("Пароли не совпадают")
#         return cd['password2']