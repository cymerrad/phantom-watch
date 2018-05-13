# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from service.models import WebpageOrder

@shared_task
def get_all_orders():
    orders = WebpageOrder.objects.all()
    return orders

@shared_task
def test_task(arg1, arg2, **kwargs):
    print("Argument 1: {}; argument 2: {}, rest: {}".format(arg1, arg2, kwargs))
    return

@shared_task
def take_screenshot(webpage_url, webpage_order):
    
    return
