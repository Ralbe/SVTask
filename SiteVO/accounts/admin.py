from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import RegisterForm

admin.site.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('phone', 'password', 'password1')}),
        (('Personal info'), {'fields': ('firstname', 'lastname')}),
        (('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('phone', 'firstname', 'lastname', 'is_staff')
    search_fields = ('phone', 'firstname', 'lastname')