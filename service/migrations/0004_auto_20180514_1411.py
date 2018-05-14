# Generated by Django 2.0.5 on 2018-05-14 14:11

from django.db import migrations, models
import service.models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0003_auto_20180513_1455'),
    ]

    operations = [
        migrations.AlterField(
            model_name='webpageorder',
            name='crontab',
            field=models.CharField(max_length=50, validators=[service.models.validate_crontab]),
        ),
    ]
