# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Picture(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    pic = models.ImageField(upload_to='pic_folder/')
    order = models.ForeignKey('service.WebpageOrder', related_name='pictures', on_delete=models.CASCADE)
    