# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from uuid import uuid4
import logging
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
import uuid
from celery.schedules import crontab
from django_celery_beat.models import PeriodicTask, CrontabSchedule, IntervalSchedule
import json
from datetime import datetime, timedelta
from django.utils import timezone
from croniter import croniter
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import URLValidator
import daemon.tasks

# logger = logging.getLogger(__name__)
logger = logging.getLogger('django')

def scramble_uploaded_filename(instance, filename):
    """
    Scramble / uglify the filename of the uploaded file, but keep the files extension (e.g., .jpg or .png)
    :param instance:
    :param filename:
    :return:
    """
    extension = filename.split(".")[-1]
    return '{}.{}'.format(uuid4(), extension)

class Screenshot(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    pic = models.ImageField("Uploaded image", upload_to=scramble_uploaded_filename)
    order = models.ForeignKey('daemon.WebpageOrder', related_name='screenshots', on_delete=models.CASCADE)
    original_filename = models.TextField("Original filename", default="")
    description = models.TextField("Description of the uploaded image", default="")

    class Meta:
        ordering = ('created',) 

def validate_crontab(ctab: str):
    if not croniter.is_valid(ctab):
        raise ValidationError(
            _('%(value)s is not a valid UNIX crontab entry'),
            params={'value': ctab},
        )
    
def parse_crontab(ctab: str):
    spl = ctab.split(' ')
    return {'minute':spl[0], 'hour':spl[1], 'day_of_month':spl[2], 'month_of_year':spl[3], 'day_of_week':spl[4]}

def datetime_2_crontab(dtime: datetime):
    return "{M} {H} {d} {m} {w}".format(
        M = dtime.minute,
        H = dtime.hour,
        d = dtime.day,
        m = dtime.month,
        w = '*'
    )

class ScreenshotBatchParent(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey('daemon.WebpageOrder', related_name='screenshots_batch', on_delete=models.CASCADE)
    description = models.TextField("Parent of many single child screenshots", default="")

    class Meta:
        ordering = ('created',) 

class ScreenshotBatchChild(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    pic = models.ImageField("Uploaded image", upload_to=scramble_uploaded_filename)
    parent = models.ForeignKey(ScreenshotBatchParent, related_name='children', on_delete=models.CASCADE)
    original_filename = models.TextField("Original filename", default="")
    description = models.TextField("Description of the uploaded image", default="")

    class Meta:
        ordering = ('created',) 

class FailedScreenshot(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey('daemon.WebpageOrder', related_name='failures', on_delete=models.CASCADE)
    failure_date = models.TextField('When the failure occured', default="")
    description = models.TextField("Description of the uploaded image", default="")

class WebpageOrder(models.Model):
    WHOLE = "WHOLE"
    PARTED = "PARTED"
    TYPE_CHOICES = (
        (WHOLE, 'Whole page'),
        (PARTED, 'In parts wrt resolution'),
    )

    RESOLUTION_DEFAULT = ('1366,768')
    RESOLUTION_CHOICES = (
        (RESOLUTION_DEFAULT, '1366x768'),
        ('1920,1080', '1920x1080'),
        ('1280,800', '1280x800'),
        ('320,568', '320x568'),
        ('1440,900', '1440x900'),
        ('1280,1024', '1280x1024'),
        ('320,480', '320x480'),
        ('1600,900', '1600x900'),
        ('768,1024', '768x1024'),
        ('1024,768', '1024x768'),
        ('1680,1050', '1680x1050'),
    )

    created = models.DateTimeField(auto_now_add=True)
    target_url = models.CharField(max_length=2083, blank=False, validators=[URLValidator])
    owner = models.ForeignKey('auth.User', related_name='orders', on_delete=models.CASCADE)
    crontab = models.CharField(max_length=1024, blank=False, validators=[validate_crontab])
    schedule = models.ForeignKey('daemon.TaskScheduler', on_delete=models.SET_NULL, null=True)
    shot_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=WHOLE)
    resolution = models.CharField(max_length=20, choices=RESOLUTION_CHOICES, default=RESOLUTION_DEFAULT)
    clear_view = models.BooleanField(default=False)
    username = models.CharField(max_length=50, default="")
    password = models.CharField(max_length=50, default="")

    def save(self, *args, **kwargs):
        """
        When created/updated create/update an order in Celery's crontab
        """
        if self.pk is None:
            super(WebpageOrder, self).save(*args, **kwargs)
            self.save()
        else:
            if self.schedule:
                sch = self.schedule
                sch.terminate()

            whole_page = True if self.shot_type == WebpageOrder.WHOLE else False

            self.schedule = TaskScheduler.schedule_cron(
                task_name='daemon.tasks.take_screenshot', 
                crontable=self.crontab, 
                args=[self.target_url, self.pk, whole_page],
                kwargs={
                    "dimensions": self.resolution,
                    "username": self.username,
                    "password": self.password,
                    "clear_view": True if self.clear_view else False,
                }
            )
            super(WebpageOrder, self).save(*args, **kwargs)


    def delete(self, *args, **kwargs):
        sch = self.schedule
        sch.terminate()
        super(WebpageOrder, self).delete(*args, **kwargs)

    def is_whole_type(self):
        if self.shot_type == WebpageOrder.WHOLE:
            return True
        return False
    
    class Meta:
        ordering = ('created',) 
    

class TaskScheduler(models.Model):
    periodic_task = models.ForeignKey(PeriodicTask, on_delete=models.PROTECT)

    @staticmethod
    def schedule_every(task_name, period, every, args=[], kwargs={}):
        """ schedules a task by name every "every" "period". So an example call would be:
            TaskScheduler('seconds', 'mycustomtask', 30, [1,2,3]) 
            that would schedule your custom task to run every 30 seconds with the arguments 1,2 and 3 passed to the actual task. 
        """
        permissible_periods = ['hours', 'days', 'seconds', 'minutes']
        if period not in permissible_periods:
            raise Exception('Invalid period specified')
        # create the periodic task and the interval
        ptask_name = "%s_%s" % (task_name, datetime.now()) # create some name for the period task
        interval_schedules = IntervalSchedule.objects.filter(period=period, every=every)
        if interval_schedules: # just check if interval schedules exist like that already and reuse em
            interval_schedule = interval_schedules[0]
        else: # create a brand new interval schedule
            interval_schedule = IntervalSchedule()
            interval_schedule.every = every # should check to make sure this is a positive int
            interval_schedule.period = period 
            interval_schedule.save()
        ptask = PeriodicTask(name=ptask_name, task=task_name, interval=interval_schedule)
        if args:
            ptask.args = args
        if kwargs:
            ptask.kwargs = kwargs
        ptask.save()
        return TaskScheduler.objects.create(periodic_task=ptask)

    @staticmethod
    def schedule_cron(task_name, crontable, args=[], kwargs={}):
        """
        Schedules a task using UNIX cron table. E.g. "* * * * *" is every minute, "0 * * * *" every hour with 0 minutes.
        Idk, google it or read a manual for it.
        """
        parsed = parse_crontab(crontable)
        schedule, _ = CrontabSchedule.objects.get_or_create(
            **parsed
        )
        ptask_name = "%s_%s" % (task_name, datetime.now()) # create some name for the period task
        ptask = PeriodicTask(
            crontab=schedule,
            name=ptask_name,
            task=task_name,
            args=json.dumps([x for x in args]),
            kwargs=json.dumps(dict(kwargs))
        )
        ptask.save()
        return TaskScheduler.objects.create(periodic_task=ptask)

    @staticmethod
    def schedule_once(task_name, when, args, kwargs):
        """
        Schedules the task to be done only once (when)
        """


    def stop(self):
        """pauses the task"""
        ptask = self.periodic_task
        ptask.enabled = False
        ptask.save()

    def start(self):
        """starts the task"""
        ptask = self.periodic_task
        ptask.enabled = True
        ptask.save()

    def terminate(self):
        self.stop()
        ptask = self.periodic_task
        self.delete()
        ptask.delete()


class ZippingOrder(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateTimeField(blank=False)
    owner = models.ForeignKey('auth.User', related_name='zipping_orders', on_delete=models.CASCADE)
    order = models.ForeignKey(WebpageOrder, related_name='zipping_orders', on_delete=models.CASCADE)
    zip_file = models.FileField(blank=True)
    download_url = models.URLField(blank=True)
    screenshot_ranges = models.TextField(blank=True)
    screenshot_list = models.TextField(blank=True)
    all_screenshots = models.BooleanField(default=False)

    def clean(self, *args, **kwargs):
        # add custom validation here
        super(ZippingOrder, self).clean(*args, **kwargs)

    def save(self, *args, **kwargs):

        #FIXME
        # exp_date = (datetime.now() + timedelta(hours=settings.ZIP_FILE_EXPIRATION))
        exp_date = (datetime.now() + timedelta(minutes=1))
        self.expiration_date = timezone.make_aware(exp_date)
        self.full_clean()
        
        super(ZippingOrder, self).save(*args, **kwargs)
        # we now have a pk

        crontab = datetime_2_crontab(exp_date)

        # celery execute zipping job now
        daemon.tasks.zip_screenshots.delay(self.pk)

        # register deleting the zip file in a day
        TaskScheduler.schedule_cron(
            task_name='daemon.tasks.delete_file', 
            crontable=crontab, 
            args=[self.pk],
        )


    class Meta:
        ordering = ('created',) 