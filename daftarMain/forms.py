from django import forms
from .models import OfficeUser

class OfficeUserForm(forms.ModelForm):
    class Meta:
        model = OfficeUser
        fields = ['first_name', 'last_name', 'phone', 'home_phone', 'birth_date', 'code_meli', 'staff_number', 'staff_pic', 'address']
