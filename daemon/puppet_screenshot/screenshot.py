import logging
import shlex
import signal
import datetime
import time
import os
import subprocess
import errno
from django.conf import settings

# Macros
SHELL_EXECUTION_OK = 0
SHELL_EXECUTION_ERROR = 1

class ScreenshotException(Exception):
    pass

logger = logging.getLogger('django')
def with_timeout(output_filename, webpage_url, timeout, dimensions=None, whole_page=True, username=None, password=None, clear_view=False):
    cmd_parameters = [ 
        settings.NODEJS,
        settings.SCREENSHOT_JS,
        "-d", settings.SCREENSHOTS_DIR,
    ]

    if dimensions:
        cmd_parameters.append('s {},{}'.format(int(dimensions[0]), int(dimensions[1])))

    if whole_page:
        cmd_parameters.append('--whole')

    if username and password:
        cmd_parameters.append('-u {} -p {}'.format(username, password))

    if clear_view:
        cmd_parameters.append('--clear')

    cmd_parameters.append('-o {filename} {page}'.format(filename=output_filename, page=webpage_url))
    cmd = " ".join(cmd_parameters)

    start = datetime.datetime.now()
    
    p = subprocess.Popen(shlex.split(cmd), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # timeout
    while p.poll() is None:
        time.sleep(0.1)
        now = datetime.datetime.now()
        if (now - start).seconds > timeout:
            logger.debug("Shell command PID {} reached the timeout, killing it now".format(p.pid))
            
            if sys.platform == 'win32':
                p.send_signal(signal.SIGTERM)
            else:
                p.send_signal(signal.SIGKILL)
            
            raise ScreenshotException("PID {} reached timeout".format(p.pid))
    
    retval = p.poll()
    if retval != SHELL_EXECUTION_OK:
        # error
        logger.debug("PID {} returned\nstdout: '{}'\nstderr: '{}';".format(p.pid, p.stdout.read(), p.stderr.read())) 
        raise ScreenshotException("Unknown exception")
    
    else:
        # ok
        output = p.stdout.read()
        logger.debug("PID {} returned".format(str(output)))
        return output
