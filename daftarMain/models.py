from django.db import models

class Product(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    last_update = models.DateTimeField(auto_now=True)


class User(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=255)
    birth_date = models.DateField(null=True)

    