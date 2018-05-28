# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from daemon.models import WebpageOrder, Screenshot, FailedScreenshot, ScreenshotBatchParent, ScreenshotBatchChild
from uuid import uuid4
from django.conf import settings
from django.core.files.images import ImageFile as DjangoImage
from django.core.files.uploadedfile import UploadedFile
from daemon.puppet_screenshot.screenshot import with_timeout
from datetime import datetime
import logging
import os
import json

logger = logging.getLogger('django')

@shared_task
def take_screenshot(webpage_url, webpage_order_id, whole_page, **kwargs):
    """
    kwargs:
    dimensions=None, 
    whole_page=True, 
    username=None, 
    password=None, 
    clear_view=False
    """
    output_filename = os.path.join('{}.png'.format(uuid4()))
    timeout = settings.SCREENSHOT_TIMEOUT

    try:
        result = with_timeout(output_filename, webpage_url, timeout, whole_page=whole_page, **kwargs)
    except Exception as e:
        logger.error("Screenshot script raised an exception: {}".format(e))
        return e

    ### SAVE TO DB
    try:
        # TODO
        # from daemon.tasks import take_screenshot as ts
        # ts.run('http://example.com', 0)
        # PARSING THE RESULT
        pre_json = result.decode('utf-8').strip()
        structure = json.loads(pre_json)
        assert len(structure) == 1 # I made the .js script so it would accept many inputs, but for now we pass only one
        output_info = structure[0] # e.g. [{'location': '/tmp/screenshots/6e14ea74-8072-4369-8b9b-7962acc3cdc4.png', 'datetime': '2018-04-05T15:43:18'}]

        webpage_order = WebpageOrder.objects.get(id=webpage_order_id)

        # WHOLE_PAGE
        if whole_page:
            assert len(output_info) == 1
            screen = output_info[0]

            try: 
                err = screen['error']
                try:
                    date = screen['datetime']
                except KeyError:
                    date = "This failed too?"
                failure = FailedScreenshot(order=webpage_order, failure_date=date, description=err)
                failure.save()

            # so this is okay, as it means no error!
            except KeyError as e:
                try:
                    location = screen['location']
                    date = screen['datetime']
                except KeyError:
                    logger.error("Complete failure of the system. Screenshot output: {}".format(pre_json))

                with open(location, "rb") as fp:
                    wrapped_file = UploadedFile(fp)
                    pic = Screenshot(pic=wrapped_file, order=webpage_order, original_filename=output_filename,
                        description="Screenshot of {} from {}".format(webpage_url, date))
                    pic.save()
        # PARTED_PAGE
        else:
            desc = "Batch of screenshots containing {} elements.".format(len(output_info))
            parent = ScreenshotBatchParent.objects.create(order=webpage_order, description=desc)

            for screen in output_info:
                try: 
                    err = screen['error']
                    try:
                        date = screen['datetime']
                    except KeyError:
                        date = "This failed too?"
                    failure = FailedScreenshot(order=webpage_order, failure_date=date, description=err)
                    failure.save()

                # so this is okay, as it means no error!
                except KeyError as e:
                    try:
                        location = screen['location']
                        date = screen['datetime']
                    except KeyError:
                        logger.error("Complete failure of the system. Screenshot output: {}".format(pre_json))
                        continue

                    with open(location, "rb") as fp:
                        wrapped_file = UploadedFile(fp)
                        pic = ScreenshotBatchChild(pic=wrapped_file, parent=parent, original_filename=output_filename,
                            description="Screenshot of {} from {}".format(webpage_url, date))
                        pic.save()
            
    except Exception as e:
        msg = "Unexpected error receiving the screenshot: {}\n{}".format(e, pre_json)
        logger.error(msg)
        webpage_order = WebpageOrder.objects.get(id=webpage_order_id)
        failure = FailedScreenshot(order=webpage_order, failure_date=str(datetime.now()), description=msg)
        failure.save()

    return pre_json


