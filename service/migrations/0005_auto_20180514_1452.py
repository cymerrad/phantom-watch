# Generated by Django 2.0.5 on 2018-05-14 14:52

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0004_auto_20180514_1411'),
    ]

    operations = [
        migrations.AlterField(
            model_name='webpageorder',
            name='url',
            field=models.CharField(max_length=2083, validators=[django.core.validators.URLValidator]),
        ),
    ]