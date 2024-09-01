from django import forms
from .models import OfficeUser,RegularRequest,Project,Leave
from django_jalali.forms.widgets import jDateInput, jDateTimeInput

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

class LeaveForm(forms.ModelForm):
    class Meta:
        model = Leave
        fields = ['leave_type', 'start_time', 'end_time', 'start_date', 'end_date', 'reason']
        widgets = {
            'start_time': jDateTimeInput(format='%Y-%m-%d %H:%M'),
            'end_time': jDateTimeInput(format='%Y-%m-%d %H:%M'),
            'start_date': jDateInput(format='%Y-%m-%d'),
            'end_date': jDateInput(format='%Y-%m-%d'),
        }

    def clean(self):
        cleaned_data = super().clean()
        leave_type = cleaned_data.get('leave_type')

        if leave_type == 'hourly':
            start_time = cleaned_data.get('start_time')
            end_time = cleaned_data.get('end_time')
            if not start_time or not end_time:
                raise forms.ValidationError('Both start and end time are required for hourly leave.')

        elif leave_type == 'daily':
            start_date = cleaned_data.get('start_date')
            end_date = cleaned_data.get('end_date')
            if not start_date or not end_date:
                raise forms.ValidationError('Both start and end date are required for daily leave.')

        return cleaned_data