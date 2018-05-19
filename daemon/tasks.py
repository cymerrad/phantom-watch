# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from daemon.models import WebpageOrder, Picture
from uuid import uuid4
from django.conf import settings
from django.core.files.images import ImageFile as DjangoImage
from django.core.files.uploadedfile import UploadedFile
from daemon.webscreenshot import single_screenshot
import datetime
import logging
import os

logger = logging.getLogger('django')

@shared_task
def take_screenshot(webpage_url, webpage_order_id, **kwargs):
    output_filename = os.path.join(settings.SCREENSHOTS_DIRECTORY, ('%s.png' % uuid4()))

    # constants in code (Y)
    timeout = 30

    try:
        result = single_screenshot.with_timeout(output_filename, webpage_url, timeout)
    except Exception as e:
        logger.error("Screenshot script raised an exception: {}".format(e))

    if result is single_screenshot.SHELL_EXECUTION_OK:    
        ### SAVE TO DB
        try:
            webpage_order = WebpageOrder.objects.get(id=webpage_order_id)

            with open(output_filename, "rb") as fp:
                wrapped_file = UploadedFile(fp)
                pic = Picture(pic=wrapped_file, order=webpage_order, original_filename=output_filename,
                    description="Screenshot of {} from {}".format(webpage_url, datetime.datetime.now()))
                pic.save()
                return 0

        except Exception as e:
            logger.error("Reading/saving the screenshot: {}".format(e))

    # otherwise screenshot failed
    # maybe you should do something about it?

    # TODO errors table?

    return 1


