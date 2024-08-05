from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class OfficeManager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True) # remove null, blank = true
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone = models.CharField(max_length=15, unique=True)
    birth_date = models.DateField(null=True, blank=True)
    code_meli = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class OfficeUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True) # remove null, blank = true
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone = models.CharField(max_length=15, unique=True)
    home_phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    code_meli = models.CharField(max_length=10)
    office_admin = models.ForeignKey(OfficeManager, on_delete=models.CASCADE, null=True, blank=True) # remove null, blank = true
    staff_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    staff_pic = models.ImageField(upload_to='staff_pics/', null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Clock(models.Model):
    entry_to_office = models.DateTimeField(null=True, blank=True)
    exit_from_office = models.DateTimeField(null=True, blank=True)
    wait_time_start = models.DateTimeField(null=True, blank=True)
    wait_time_finish = models.DateTimeField(null=True, blank=True)
    office_user = models.ForeignKey(OfficeUser, on_delete=models.CASCADE, null=True, blank=True) # remove null, blank = true

    def __str__(self):
        return f"{self.office_user} - {self.entry_to_office}"
