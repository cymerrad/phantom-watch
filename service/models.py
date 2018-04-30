from django.db import models
from django.contrib.auth.models import User
import uuid

# Create your models here.
class WebpageOrder(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    url = models.CharField(max_length=2083, blank=False)
    owner = models.ForeignKey('auth.User', related_name='orders', on_delete=models.CASCADE)

    class Meta:
        ordering = ('created',) 
