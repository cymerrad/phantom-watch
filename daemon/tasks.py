# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from daemon.models import WebpageOrder, Picture
from uuid import uuid4
from django.conf import settings
import logging
import shlex
import signal
import datetime
import time
import os
import subprocess
import errno
from django.core.files.images import ImageFile as DjangoImage
from django.core.files.uploadedfile import UploadedFile

@shared_task
def get_all_orders():
    orders = WebpageOrder.objects.all()
    return orders

@shared_task
def test_task(arg1, arg2, **kwargs):
    print("Argument 1: {}; argument 2: {}, rest: {}".format(arg1, arg2, kwargs))
    return

# Macros
SHELL_EXECUTION_OK = 0
SHELL_EXECUTION_ERROR = -1
PHANTOMJS_HTTP_AUTH_ERROR_CODE = 2

@shared_task
def take_screenshot(webpage_url, webpage_order_id, **kwargs):
    output_filename = os.path.join(settings.SCREENSHOTS_DIRECTORY, ('%s.png' % uuid4()))
    cmd_parameters = [ settings.PHANTOMJS_BIN,
                    '--ignore-ssl-errors true',
                    '--ssl-protocol any',
                    '--ssl-ciphers ALL'
    ]
    cmd_parameters.append('"%s" url_capture="%s" output_file="%s"' % (settings.WEBSCREENSHOT_JS, webpage_url, output_filename))
    cmd = " ".join(cmd_parameters)

    # constants in code (Y)
    timeout = 30
    logger_url = logging.getLogger('django')
    start = datetime.datetime.now()
    
    try:
        p = subprocess.Popen(shlex.split(cmd), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Phantomjs timeout
        while p.poll() is None:
            time.sleep(0.1)
            now = datetime.datetime.now()
            if (now - start).seconds > timeout:
                logger_url.debug("Shell command PID %s reached the timeout, killing it now" % p.pid)
                logger_url.error("Screenshot somehow failed\n")
                
                if sys.platform == 'win32':
                    p.send_signal(signal.SIGTERM)
                else:
                    p.send_signal(signal.SIGKILL)
                
                return SHELL_EXECUTION_ERROR
        
        retval = p.poll()
        if retval != SHELL_EXECUTION_OK:
            if retval == PHANTOMJS_HTTP_AUTH_ERROR_CODE:
                # HTTP Authentication request
                logger_url.error("HTTP Authentication requested, try to pass credentials with -u and -b options")
            else:
                # Phantomjs general error
                logger_url.error("Shell command PID %s returned an abnormal error code: '%s'" % (p.pid,retval))
                logger_url.error("Screenshot somehow failed\n")
                    
            return SHELL_EXECUTION_ERROR
        
        else:
            # Phantomjs ok
            logger_url.debug("Shell command PID %s ended normally" % p.pid)
            logger_url.info("Screenshot OK\n")

            ### SAVE TO DB
            try:
                webpage_order = WebpageOrder.objects.get(id=webpage_order_id)

                with open(output_filename, "rb") as fp:
                    wrapped_file = UploadedFile(fp)
                    pic = Picture(pic=wrapped_file, order=webpage_order, original_filename=output_filename,
                        description="Screenshot of {} from {}".format(webpage_url, datetime.datetime.now()))
                    pic.save()
            except Exception as e:
                logger_url.error("Reading the screenshot: {}".format(e))
            ###

            return SHELL_EXECUTION_OK
    
    except Exception as e:
        try:
            if e.errno and e.errno == errno.ENOENT :
                logger_url.error('phantomjs binary could not have been found in your current PATH environment variable, exiting')
        except AttributeError as e:
            pass
        else:
            logger_url.error('Unknown error: %s, exiting' % e )
        return SHELL_EXECUTION_ERROR

