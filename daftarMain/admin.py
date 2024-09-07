from django.contrib import admin
from .models import OfficeManager, OfficeUser
from jalali_date import datetime2jalali, date2jalali
from jalali_date.admin import ModelAdminJalaliMixin

@admin.register(OfficeManager)
class OfficeManagerAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'get_birth_date_jalali', 'code_meli')

    # Convert birth_date to Jalali in the admin display
    @admin.display(description='تاریخ تولد')
    def get_birth_date_jalali(self, obj):
        if obj.birth_date:
            return date2jalali(obj.birth_date).strftime('%Y/%m/%d')
        return '-'

@admin.register(OfficeUser)
class OfficeUserAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone', 'home_phone', 'get_birth_date_jalali', 'code_meli', 'office_admin')

    # Convert birth_date to Jalali in the admin display
    @admin.display(description='تاریخ تولد')
    def get_birth_date_jalali(self, obj):
        if obj.birth_date:
            return date2jalali(obj.birth_date).strftime('%Y/%m/%d')
        return '-'
