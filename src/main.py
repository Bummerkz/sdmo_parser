#-*- coding:utf-8 -*-
# from URMessageChannel import TimerEvtHandle, init_base, logconfig
# import fc

import sys
import config

# New version
from datetime import datetime
from logging import getLogger, Formatter, DEBUG
from logging.handlers import RotatingFileHandler

from http_server import HTTPServer

from processor import Processor

from time import sleep

# DEV flag for PC debugging
DEV = True

# modbus_lock = threading.Lock()

if DEV:
    APP_PATH = ""
    MYAPP_NAME = ""
else:
    APP_PATH = "/usr/pyuser/app/"
    MYAPP_NAME = "sdmo_parser/"

# New features for device manager
VERSION = '0.1.0'

LOG_PATH = APP_PATH + MYAPP_NAME + 'logs'
LOGGER_NAME = 'main'

HTTP_SERVER_ADDR = ('', 81)

CFG = config.get_config(dev=True)

# Logger init
def prepare_logger():
    logger = getLogger(LOGGER_NAME)
    logger.setLevel(DEBUG)
    handler = RotatingFileHandler(LOG_PATH + '\\' + 'main.log', maxBytes=10485760,
                                  backupCount=20)
    formatter = Formatter(u'[%(asctime)s][%(threadName)s][%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

def start_app():

    logger = prepare_logger()
    logger.info('Started version %s at %s' % (VERSION, datetime.now()))

    http_server = HTTPServer(HTTP_SERVER_ADDR)
    http_server.start_serve()

    # processor = Processor(deviceCommunicate.get_queue(), http_server.queue, CFG)
    # processor.start()

    while 1:
        try:
            if processor.is_running():
                sleep(1)
            else:
                processor.stop()
                processor.start()
        except KeyboardInterrupt:
            processor.stop()
            http_server.server_close()
            deviceCommunicate._stop_listen()
            exit(0)

    
def main(argv=sys.argv):

    start_app()


if __name__=='__main__':
    main()