from django import forms
from .models import OfficeUser,RegularRequest,Project

class OfficeUserForm(forms.ModelForm):
    class Meta:
        model = OfficeUser
        fields = [
            'first_name', 'last_name', 'birth_date',
            'code_meli', 'home_phone', 'phone',
            'staff_number', 'address', 'staff_pic', 'have_bime'
        ]
        
class RegularRequestForm(forms.ModelForm):
    class Meta:
        model = RegularRequest
        fields = ['request_type', 'message']
        widgets = {
            'request_type': forms.Select(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }

class ProjectForm(forms.ModelForm):
    assigned_users = forms.ModelMultipleChoiceField(
        queryset=OfficeUser.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Assign Office Users"
    )

    class Meta:
        model = Project
        fields = ['name', 'description', 'start_date', 'end_date', 'assigned_users']

class ProjectSelectionForm(forms.Form):
    projects = forms.ModelMultipleChoiceField(
        queryset=Project.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )