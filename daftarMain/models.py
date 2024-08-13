from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class OfficeManager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True) # remove null, blank = true
    full_name = models.CharField(max_length=50,null=True,blank=True)
    phone = models.CharField(max_length=15, unique=True)
    birth_date = models.DateField(null=True, blank=True)
    code_meli = models.CharField(max_length=10, null=True, blank=True)
    email = models.EmailField(max_length=254, null=True, blank=True)

    def __str__(self):
        return f"{self.full_name}"

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
    have_bime = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Clock(models.Model):
    entry_to_office = models.DateTimeField(null=True, blank=True)
    exit_from_office = models.DateTimeField(null=True, blank=True)
    office_user = models.ForeignKey(OfficeUser, on_delete=models.CASCADE, null=True, blank=True) # remove null, blank = true
    projects = models.ManyToManyField('Project', related_name="clock_entries", blank=True)

    def __str__(self):
        return f"{self.office_user} - {self.entry_to_office}"

class Leave(models.Model):
    office_user = models.ForeignKey(OfficeUser, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=10, choices=[('hourly', 'Hourly'), ('daily', 'Daily')])
    # hourly leave    
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    # daily leave fields
    start_date = models.DateField(null=True, blank=True)  
    end_date = models.DateField(null=True, blank=True)   

    reason = models.TextField(null=True, blank=True)
    approved = models.BooleanField(default=None, null=True, blank=True)

    def __str__(self):
        return f"{self.office_user} - {self.leave_type} leave from {self.start_date or self.start_time} to {self.end_date or self.end_time}"
    
class RegularRequest(models.Model):
    REQUEST_TYPES = [
        ('complaint', 'Complaint'),
        ('suggestion', 'Suggestion'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(OfficeUser, on_delete=models.CASCADE)
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPES)
    message = models.TextField()
    submitted_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.get_request_type_display()} by {self.user.first_name} {self.user.last_name} on {self.submitted_at}"

class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    assigned_users = models.ManyToManyField(OfficeUser, related_name='projects')

    def __str__(self):
        return self.name

    def total_hours(self):
        return sum(log.hours_spent for log in self.projecttimelog_set.all())

    
class ProjectTimeLog(models.Model):
    office_user = models.ForeignKey(OfficeUser, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    hours_spent = models.FloatField(default=0)
    log_date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('office_user', 'project', 'log_date')