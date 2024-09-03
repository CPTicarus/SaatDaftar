from django import forms
from .models import OfficeUser,RegularRequest,Project,Leave
from django_jalali.forms.widgets import jDateInput, jDateTimeInput

class OfficeUserForm(forms.ModelForm):
    birth_date = forms.DateField(
        required=False,
        label='تاریخ تولد'
    )

    class Meta:
        model = OfficeUser
        exclude = ['office_admin', 'user']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام خانوادگی'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'شماره موبایل'}),
            'home_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'شماره تلفن ثابت'}),
            'code_meli': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'کد ملی'}),
            'birth_date': jDateInput(attrs={'class': 'form-control', 'placeholder': 'YYYY-MM-DD'}),
            'staff_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'شماره پرسنلی'}),
            'staff_pic': forms.ClearableFileInput(attrs={'class': 'form-control', 'placeholder': 'عکس پرسنل'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'آدرس'}),
            'have_bime': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'code_bime': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'کد بیمه'}),
            'family_phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'شماره تلفن خانواده'}),
            'marital_status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'military_service_status': forms.Select(attrs={'class': 'form-control'}),
            'childeren_count': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'تعداد فرزندان'}),
        }
        labels = {
            'first_name': 'نام',
            'last_name': 'نام خانوادگی',
            'phone': 'شماره موبایل',
            'home_phone': 'شماره تلفن ثابت',
            'code_meli': 'کد ملی',
            'staff_number': 'شماره پرسنلی',
            'staff_pic': 'عکس پرسنل',
            'address': 'آدرس',
            'have_bime': 'آیا بیمه دارید؟',
            'code_bime': 'کد بیمه',
            'family_phone_number': 'شماره تلفن خانواده',
            'marital_status': 'وضعیت تاهل',
            'military_service_status': 'وضعیت خدمت سربازی',
            'childeren_count': 'تعداد فرزندان',
        }


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

    start_date = forms.DateField(
        widget=jDateInput(attrs={'class': 'form-control', 'placeholder': 'تاریخ شروع'}),
        required=True,
        label='تاریخ شروع'
    )

    end_date = forms.DateField(
        widget=jDateInput(attrs={'class': 'form-control', 'placeholder': 'تاریخ پایان'}),
        required=False,
        label='تاریخ پایان'
    )

    class Meta:
        model = Project
        fields = ['name', 'description', 'start_date', 'end_date', 'assigned_users']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class ProjectSelectionForm(forms.Form):
    projects = forms.ModelMultipleChoiceField(
        queryset=Project.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )


class LeaveForm(forms.ModelForm):
    start_time = forms.DateTimeField(
        widget=jDateTimeInput(format='%Y-%m-%d %H:%M', attrs={'class': 'form-control', 'placeholder': 'زمان شروع'}),
        required=False,
        label='زمان شروع'
    )

    end_time = forms.DateTimeField(
        widget=jDateTimeInput(format='%Y-%m-%d %H:%M', attrs={'class': 'form-control', 'placeholder': 'زمان پایان'}),
        required=False,
        label='زمان پایان'
    )

    start_date = forms.DateField(
        widget=jDateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'placeholder': 'تاریخ شروع'}),
        required=False,
        label='تاریخ شروع'
    )

    end_date = forms.DateField(
        widget=jDateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'placeholder': 'تاریخ پایان'}),
        required=False,
        label='تاریخ پایان'
    )

    class Meta:
        model = Leave
        fields = ['leave_type', 'start_time', 'end_time', 'start_date', 'end_date', 'reason']
        widgets = {
            'leave_type': forms.Select(attrs={'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'دلیل مرخصی'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        leave_type = cleaned_data.get('leave_type')

        if leave_type == 'hourly':
            start_time = cleaned_data.get('start_time')
            end_time = cleaned_data.get('end_time')
            if not start_time or not end_time:
                raise forms.ValidationError('برای مرخصی ساعتی هر دو زمان شروع و پایان الزامی است.')

        elif leave_type == 'daily':
            start_date = cleaned_data.get('start_date')
            end_date = cleaned_data.get('end_date')
            if not start_date or not end_date:
                raise forms.ValidationError('برای مرخصی روزانه هر دو تاریخ شروع و پایان الزامی است.')

        return cleaned_data