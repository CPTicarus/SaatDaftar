# Generated by Django 5.0.7 on 2024-08-01 06:03

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Clock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entry_to_office', models.DateTimeField(auto_now=True)),
                ('exit_from_office', models.DateTimeField(auto_now=True)),
                ('wait_time_start', models.DateTimeField(auto_now=True)),
                ('wait_time_finish', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='OffceAdmin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('phone', models.CharField(max_length=255, unique=True)),
                ('birth_date', models.DateField(null=True)),
                ('code_meli', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='OfficeUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('phone', models.CharField(max_length=255, unique=True)),
                ('home_phone', models.CharField(max_length=10, null=True, unique=True)),
                ('birth_date', models.DateField(null=True)),
                ('code_meli', models.CharField(max_length=10)),
            ],
        ),
    ]
