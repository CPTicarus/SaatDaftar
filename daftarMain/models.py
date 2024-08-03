from django.db import models

class OfficeManager(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15,unique=True)
    birth_date = models.DateField(null=True)
    code_meli = models.CharField(max_length=10,null=True)


class OfficeUser(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15,unique=True)
    home_phone = models.CharField(max_length=15,unique=True,null=True)
    birth_date = models.DateField(null=True)
    code_meli = models.CharField(max_length=10)
    office_admin = models.ForeignKey(OfficeManager,on_delete=models.CASCADE)


class  Clock(models.Model):
    entry_to_office = models.DateTimeField(auto_now=True)
    exit_from_office = models.DateTimeField(auto_now=True)
    wait_time_start = models.DateTimeField(auto_now=True)
    wait_time_finish = models.DateTimeField(auto_now=True)
    office_user = models.ForeignKey( OfficeUser ,on_delete=models.CASCADE)


class Sallary(models.Model):
    monthly = models.IntegerField(max_length=12,null=True)
    