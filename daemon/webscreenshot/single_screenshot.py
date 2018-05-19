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
SHELL_EXECUTION_ERROR = -1
PHANTOMJS_HTTP_AUTH_ERROR_CODE = 2

logger_url = logging.getLogger('django')
def with_timeout(output_filename, webpage_url, timeout):
    cmd_parameters = [ settings.PHANTOMJS_BIN,
        '--ignore-ssl-errors true',
        '--ssl-protocol any',
        '--ssl-ciphers ALL'
    ]
    cmd_parameters.append('"%s" url_capture="%s" output_file="%s"' % (settings.WEBSCREENSHOT_JS, webpage_url, output_filename))
    cmd = " ".join(cmd_parameters)
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