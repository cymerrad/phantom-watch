# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from daemon.models import WebpageOrder, Picture
from uuid import uuid4
from django.conf import settings
from django.core.files.images import ImageFile as DjangoImage
from django.core.files.uploadedfile import UploadedFile
from daemon.puppet_screenshot.screenshot import with_timeout
import datetime
import logging
import os

logger = logging.getLogger('django')

@shared_task
def take_screenshot(webpage_url, webpage_order_id, **kwargs):
    output_filename = os.path.join('{}.png'.format(uuid4()))
    timeout = settings.SCREENSHOT_TIMEOUT

    try:
        result = with_timeout(output_filename, webpage_url, timeout)
    except Exception as e:
        logger.error("Screenshot script raised an exception: {}".format(e))
        return e

    ### SAVE TO DB
    try:
        # TODO
        # PARSING THE RESULT

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


