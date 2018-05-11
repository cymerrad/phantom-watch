# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

def scramble_uploaded_filename(instance, filename):
    """
    Scramble / uglify the filename of the uploaded file, but keep the files extension (e.g., .jpg or .png)
    :param instance:
    :param filename:
    :return:
    """
    extension = filename.split(".")[-1]
    return "{}.{}".format(uuid.uuid4(), extension)

# Create your models here.
class Picture(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    # pic = models.ImageField(upload_to='pic_folder/')
    pic = models.ImageField("Uploaded image", upload_to=scramble_uploaded_filename)
    order = models.ForeignKey('service.WebpageOrder', related_name='pictures', on_delete=models.CASCADE)
    original_filename = models.TextField("Original filename", default="")
    description = models.TextField("Description of the uploaded image", default="")

    def __str__(self):
        return self.original_filename

    