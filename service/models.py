from django.db import models
from django.contrib.auth.models import User
import uuid
from celery.schedules import crontab
from django_celery_beat.models import PeriodicTask, CrontabSchedule
import json
from datetime import datetime, timedelta
from croniter import croniter
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import URLValidator

def validate_crontab(ctab: str):
    if not croniter.is_valid(ctab):
        raise ValidationError(
            _('%(value)s is not a valid UNIX crontab entry'),
            params={'value': ctab},
        )
    
def parse_crontab(ctab: str):
    spl = ctab.split(' ')
    return {'minute':spl[0], 'hour':spl[1], 'day_of_month':spl[2], 'month_of_year':spl[3], 'day_of_week':spl[4]}

class WebpageOrder(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    url = models.CharField(max_length=2083, blank=False, validators=[URLValidator])
    owner = models.ForeignKey('auth.User', related_name='orders', on_delete=models.CASCADE)
    crontab = models.CharField(max_length=50, blank=False, validators=[validate_crontab])

    def save(self, *args, **kwargs):
        """
        When created/updated create/update an order in Celery's crontab
        """
        super(WebpageOrder, self).save(*args, **kwargs)

        parsed = parse_crontab(self.crontab)
        schedule, _ = CrontabSchedule.objects.get_or_create(
            **parsed
        )
        PeriodicTask.objects.create(
            crontab=schedule,
            name=self.pk,
            task='daemon.tasks.take_screenshot',
            args=json.dumps([self.url, self.pk]),
            kwargs=json.dumps(parsed),
            # expires=datetime.utcnow() + timedelta(minutes=5)
        )


    
    class Meta:
        ordering = ('created',) 
    
    