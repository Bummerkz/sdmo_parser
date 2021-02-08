#-*- coding:utf-8 -*-
import sys
from URMessageChannel import TimerEvtHandle, init_base, logconfig
import server
import threading
import logging
import config
import fc
import merc
import os

modbus_lock = threading.Lock()
APP_PATH = "/usr/pyuser/app/"
MYAPP_NAME = "sdmo_parser/"

class startWork(TimerEvtHandle):
    def __init__(self, sec, cfg, last_mtime):  # Trigger timer after "sec" seconds
        self.base = init_base()
        self.cfg = cfg
        self.last_mtime = last_mtime
        TimerEvtHandle.__init__(self, self.base, sec)

    def timerHandle(self, evt, userdata):
        t = os.path.getmtime(APP_PATH + MYAPP_NAME + "config.json")

        current_mtime = t
        if t > self.last_mtime: # если файл изменился обновляем конфиг
            self.cfg = config.get_config()
            # Создаем инстансы устроиств из файла конфигурации
            for device in self.cfg["Devices"]:
                if self.cfg["Devices"][device]['name'].lower() == 'fc':
                    interval = int(self.cfg['Devices'][device]['send_interval'])
                    app = fc.InitTimer(interval, device)
                    t = threading.Thread(target=app.start)
                    t.daemon = True
                    t.start()
                    logging.info('FC device created!')
                elif self.cfg["Devices"][device]['name'].lower() == 'mercury':
                    # interval = int(self.cfg['Devices'][device]['send_interval'])
                    # app = merc.InitTimer(interval, device)
                    # t = threading.Thread(target=app.start)
                    # t.daemon = True
                    # t.start()
                    logging.info('Mercury device created!')

        self.last_mtime = current_mtime

        self.startTimer()


def start_app():
    # Запускаем сервер
    local_server = server
    server_thread = threading.Thread(target=local_server.StartServer)
    server_thread.start()

    cfg = config.get_config()
    last_mtime = None

    worker_thread = startWork(10, cfg, last_mtime)
    worker_thread = threading.Thread(target=worker_thread.start)
    worker_thread.start()


def main(argv=sys.argv):
    # logconfig('info')	#set log level，such as "info"

    #instantiates a startWork object and start event loop or invoke start_app() directly
    start_app()


if __name__=='__main__':
    main()