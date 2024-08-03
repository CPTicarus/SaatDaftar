from django.contrib import admin
from .models import OfficeManager, OfficeUser

@admin.register(OfficeManager)
class OfficeManagerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone', 'birth_date', 'code_meli')

@admin.register(OfficeUser)
class OfficeUserAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone', 'home_phone', 'birth_date', 'code_meli', 'office_admin')
