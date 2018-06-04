# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
import daemon.models
from uuid import uuid4
from django.conf import settings
from django.core.files.images import ImageFile as DjangoImage
from django.core.files.uploadedfile import UploadedFile
from daemon.puppet_screenshot.screenshot import with_timeout
from datetime import datetime
import logging
import os
import json
from time import sleep

logger = logging.getLogger('django')

FAILURE=False
SUCCESS=True

@shared_task
def take_screenshot(webpage_url, webpage_order_id, whole_page, **kwargs):
    """
    kwargs:
    dimensions=None, 
    username=None, 
    password=None, 
    clear_view=False
    """
    output_filename = os.path.join('{}.png'.format(uuid4()))
    timeout = settings.SCREENSHOT_TIMEOUT

    try:
        result = with_timeout(output_filename, webpage_url, timeout, whole_page=whole_page, **kwargs)
    except Exception as e:
        logger.error("daemon.models.Screenshot script raised an exception: {}".format(e))
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

        webpage_order = daemon.models.WebpageOrder.objects.get(id=webpage_order_id)

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
                failure = daemon.models.FailedScreenshot(order=webpage_order, failure_date=date, description=err)
                failure.save()

            # so this is okay, as it means no error!
            except KeyError as e:
                try:
                    location = screen['location']
                    date = screen['datetime']
                except KeyError:
                    logger.error("Complete failure of the system. daemon.models.Screenshot output: {}".format(pre_json))

                with open(location, "rb") as fp:
                    wrapped_file = UploadedFile(fp)
                    pic = daemon.models.Screenshot(pic=wrapped_file, order=webpage_order, original_filename=output_filename,
                        description="daemon.models.Screenshot of {} from {}".format(webpage_url, date))
                    pic.save()
        # PARTED_PAGE
        else:
            desc = "Batch of screenshots containing {} elements.".format(len(output_info))
            parent = daemon.models.ScreenshotBatchParent.objects.create(order=webpage_order, description=desc)

            for screen in output_info:
                try: 
                    err = screen['error']
                    try:
                        date = screen['datetime']
                    except KeyError:
                        date = "This failed too?"
                    failure = daemon.models.FailedScreenshot(order=webpage_order, failure_date=date, description=err)
                    failure.save()

                # so this is okay, as it means no error!
                except KeyError as e:
                    try:
                        location = screen['location']
                        date = screen['datetime']
                    except KeyError:
                        logger.error("Complete failure of the system. daemon.models.Screenshot output: {}".format(pre_json))
                        continue

                    with open(location, "rb") as fp:
                        wrapped_file = UploadedFile(fp)
                        pic = daemon.models.ScreenshotBatchChild(pic=wrapped_file, parent=parent, original_filename=output_filename,
                            description="daemon.models.Screenshot of {} from {}".format(webpage_url, date))
                        pic.save()
            
    except Exception as e:
        msg = "Unexpected error receiving the screenshot: {}\n{}".format(e, pre_json)
        logger.error(msg)
        webpage_order = daemon.models.WebpageOrder.objects.get(id=webpage_order_id)
        failure = daemon.models.FailedScreenshot(order=webpage_order, failure_date=str(datetime.now()), description=msg)
        failure.save()
        return FAILURE

    return SUCCESS


@shared_task
def zip_screenshots(zipping_order_id, screenshot_ranges='', screenshot_list=[], all_screenshots=False):
    """
    screenshot_ranges = models.TextField(blank=True)
    screenshot_list = models.TextField(blank=True)
    all_screenshots = models.BooleanField(default=False)
    """
    zipping_order = daemon.models.ZippingOrder.objects.get(id=zipping_order_id)
    webpage_order = zipping_order.order
    shot_type = webpage_order.shot_type
    if shot_type == daemon.models.WebpageOrder.WHOLE:
        screenshots = webpage_order.screenshots
    else:
        screenshots = webpage_order.screenshots_batch

    if all_screenshots:
        return true_zip_screenshots(zipping_order)

    if len(screenshot_list) > 0:
        screenshots = screenshots.filter(pk__in=screenshot_list)

    screenshot_ranges_parsed = parse_screenshot_ranges(screenshots_ranges)
    if len(screenshot_ranges_parsed) > 0:
        screenshots = screenshots.filter(pk__in=screenshot_ranges_parsed)

    logger.info("Processing {}".format(zipping_order_id))
    sleep(5)

    # convert given data into list of files we need to zip
    # webpageorder's pk from zippingorder
    # do some queries, it'll be fine

def parse_screenshot_ranges(ranges):
    # split by commas if not null
    ranges = [x.strip(' ,') for x in ranges.strip(' ,').split(',') if x]

    # split by dashes if not null
    ranges = [x.split('-') for x in ranges if x]

    # omit incorrect ranges (e.g. 9-6), then convert strings to integers
    valid = [[int(y) for y in x] for x in ranges if (len(x) == 2 and int(x[0])<=int(x[1])) or len(x) == 1]
    if valid == []:
        return range(0)

    # join all overlapping ranges
    valid.sort()

    joined = [valid[0] if len(valid[0]) == 2 else [valid[0][0], valid[0][0]]]
    for cur in valid:
        last = joined[-1]
        if len(cur) == 1:
            if cur[0] <= last[1] + 1:
                # overlap or extend
                last[1] = max(last[1], cur[0])
            else:
                # new range
                joined.append([cur[0], cur[0]])
        else:
            if cur[0] <= last[1] + 1:
                # overlap or extend
                last[1] = max(last[1], cur[1])
            else:
                # new range
                joined.append(cur)

    # TODO
    # what if we get some gigantic number and proceed to iterating over them all?

    # yield
    for r in joined:
        for x in range(r[0], r[1] + 1):
            yield x


def true_zip_screenshots(zipping_order, screenshots):

    return SUCCESS

@shared_task
def delete_file(zipping_order_id):

    # TODO
    zipping_order = daemon.models.ZippingOrder.objects.get(id=zipping_order_id)

    logger.info("Deleting file {}".format(zipping_order.zip_file))
    sleep(2)

    # delete self?
