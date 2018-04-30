from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class WebpageOrder(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    url = models.CharField(max_length=2083, blank=False)
    user = models.ForeignKey('auth.User', related_name='orders', on_delete=models.DO_NOTHING)

    class Meta:
        ordering = ('created',) 
