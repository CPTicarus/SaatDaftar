# Generated by Django 5.0.7 on 2024-08-10 05:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('daftarMain', '0011_alter_leave_approved'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leave',
            name='approved',
            field=models.BooleanField(blank=True, default=None, null=True),
        ),
    ]
