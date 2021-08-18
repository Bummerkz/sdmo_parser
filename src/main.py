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

# DEV flag for PC debugging
DEV = True

# modbus_lock = threading.Lock()

if DEV:
    APP_PATH = ""
    MYAPP_NAME = "sdmo_parser\\"
else:
    APP_PATH = "/usr/pyuser/app/"
    MYAPP_NAME = "sdmo_parser/"

# New features for device manager
VERSION = '0.1.0'

LOG_PATH = APP_PATH + MYAPP_NAME + 'logs'
LOGGER_NAME = 'main'

HTTP_SERVER_ADDR = ('', 81)

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


# class startWork(TimerEvtHandle):
#     def __init__(self, sec, cfg, last_mtime):  # Trigger timer after "sec" seconds
#         self.base = init_base()
#         self.cfg = cfg
#         self.last_mtime = last_mtime
#         TimerEvtHandle.__init__(self, self.base, sec)

    # def timerHandle(self, evt, userdata):
    #     t = os.path.getmtime(APP_PATH + MYAPP_NAME + "config.json")

    #     current_mtime = t
    #     if t > self.last_mtime: # если файл изменился обновляем конфиг
    #         self.cfg = config.get_config()
    #         # Создаем инстансы устроиств из файла конфигурации
    #         for device in self.cfg["Devices"]:
    #             # if self.cfg["Devices"][device]['name'].lower() == 'fc':
    #             interval = int(self.cfg['Devices'][device]['send_interval'])
    #             app = serial_device.InitTimer(interval, device)
    #             t = threading.Thread(target=app.start)
    #             t.daemon = True
    #             t.start()
    #             logging.info('{0} device created!'.format(self.cfg['Devices'][device]['type']))
    #             time.sleep(10)

    #     self.last_mtime = current_mtime

    #     self.startTimer()


def start_app():

    logger = prepare_logger()
    logger.info('Started version %s at %s' % (VERSION, datetime.now()))

    # Запускаем сервер
    # local_server = server
    # server_thread = threading.Thread(target=local_server.StartServer)
    # server_thread.start()

    http_server = HTTPServer(HTTP_SERVER_ADDR)
    http_server.start_serve()

    cfg = config.get_config()
    last_mtime = None

    # worker_thread = startWork(10, cfg, last_mtime)
    # worker_thread = threading.Thread(target=worker_thread.start)
    # worker_thread.start()


def main(argv=sys.argv):

    start_app()


if __name__=='__main__':
    main()