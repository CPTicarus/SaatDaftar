from django import forms
from .models import OfficeUser,RegularRequest,Project

class OfficeUserForm(forms.ModelForm):
    class Meta:
        model = OfficeUser
        exclude = ['office_admin', 'user']
        
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