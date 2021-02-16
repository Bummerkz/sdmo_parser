# -*- coding:utf-8 -*-
from comm import Modbus, RS485

import time
import config
import threading
import requests
import journal
from datetime import datetime
import logging
from URMessageChannel import TimerEvtHandle, init_base

FORMAT = ('%(asctime)-15s %(threadName)-15s'
          ' %(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.INFO)

class InitTimer(TimerEvtHandle):
    def __init__(self, interval, device):
        self.device = device
        self.interval = interval
        self.base = init_base()

        TimerEvtHandle.__init__(self, self.base, interval)

    def timerHandle(self, evt, userdata):
        while 1:
            self.cfg = config.get_config()
            self.deviceType = self.cfg["Devices"][self.device]["type"]
            if self.deviceType.lower() == 'modbus':
                self.client = Modbus(self.cfg, self.device)
                self.send_fc_data()
            elif self.deviceType.lower() == 'mercury':
                self.client = RS485(self.cfg, self.device)
                self.send_el_data()

            time.sleep(self.interval)

    def send_fc_data(self):
        now = datetime.now()
        now = unicode(now.replace(microsecond=0))
        v = ','.join(self.client.get_modbus_fc())
        r = ','.join(self.cfg["Devices"][self.device]["regs"])
        server = self.cfg["Server"]["ip"]
        port = self.cfg["Server"]["port"]
        payload = {'d': now, 'id': 'ID', 'n': self.device, 'r': r, 'v': v}
        url = 'http://{server}:{port}/data/setReg.php'.format(server=server, port=port)

        try:
            logging.info("--- Send FC data ---")
            r = requests.get(url, params=payload)
            logging.info("status code: " + str(r.status_code))
            if r.status_code != 200:
                journal.saveData(payload, self.device, self.cfg['Server']['SD_card_storage_interval'])
            else:
                try:
                    records = journal.upload(self.device)
                    for payload in records:
                        logging.info("--- Send stored data ---")
                        r = requests.get(url, params=payload[1])
                        logging.info("status code: " + str(r.status_code))
                except Exception as e:
                    logging.info("Error: {except}".format(e))
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            logging.error(e)

    def send_el_data(self):
        now = datetime.now()
        now = unicode(now.replace(microsecond=0))
        v = ','.join(self.client.get_data())
        r = ','.join(self.cfg["Devices"][self.device]["regs"])
        server = self.cfg["Server"]["ip"]
        port = self.cfg["Server"]["port"]
        payload = {'d': now, 'id': 'ID', 'n': self.device, 'r': r, 'v': v}
        url = 'http://{server}:{port}/data/setElectric.php'.format(server=server, port=port)

        try:
            logging.info("--- Send FC data ---")
            r = requests.get(url, params=payload)
            logging.info("status code: " + str(r.status_code))
            if r.status_code != 200:
                journal.saveData(payload, self.device, self.cfg['Server']['SD_card_storage_interval'])
            else:
                try:
                    records = journal.upload(self.device)
                    for payload in records:
                        logging.info("--- Send stored data ---")
                        r = requests.get(url, params=payload[1])
                        logging.info("status code: " + str(r.status_code))
                except Exception as e:
                    logging.info("Error: {e}".format(e))
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            logging.error(e)
