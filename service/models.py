from django.db import models
from django.contrib.auth.models import User
import uuid
from celery.schedules import crontab
from django_celery_beat.models import PeriodicTask, IntervalSchedule
import json
from datetime import datetime, timedelta


# Create your models here.
class WebpageOrder(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    url = models.CharField(max_length=2083, blank=False)
    owner = models.ForeignKey('auth.User', related_name='orders', on_delete=models.CASCADE)
    crontab = models.CharField(max_length=50, blank=False)

    def save(self, *args, **kwargs):
        """
        When created/updated create/update an order in Celery's crontab
        """
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=30,
            period=IntervalSchedule.SECONDS,
        )
        PeriodicTask.objects.create(
            interval=schedule,
            name='Test',
            task='daemon.tasks.test_task',
            args=json.dumps(['arg1', 'arg2']),
            kwargs=json.dumps({
            'be_careful': True,
            }),
            expires=datetime.utcnow() + timedelta(minutes=3)
        )

        super(WebpageOrder, self).save(*args, **kwargs)
    
    class Meta:
        ordering = ('created',) 
    
    