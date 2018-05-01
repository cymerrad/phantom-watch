# Generated by Django 2.0.4 on 2018-04-30 15:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('service', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Picture',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('pic', models.ImageField(upload_to='pic_folder/')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pictures', to='service.WebpageOrder')),
            ],
        ),
    ]