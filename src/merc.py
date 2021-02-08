#-*- coding:utf-8 -*-
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder

# import json
import logging
import time
import config
import threading
# import requests
from datetime import datetime
import logging
from URMessageChannel import TimerEvtHandle, init_base
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.exceptions import ModbusIOException

cfg = config.get_config()

FORMAT = ('%(asctime)-15s %(threadName)-15s'
          ' %(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.INFO)

read_lock = threading.Lock()

class InitTimer(TimerEvtHandle):
    def __init__(self, interval, device):
        self.device = device
        self.interval = interval
        self.base = init_base()
        self.port = cfg["Port"]
        self.baudrate = cfg["Devices"][device]["baudrate"]
        self.bytesize = cfg["Devices"][device]["bytesize"]
        self.parity = cfg["Devices"][device]["parity"]
        self.stopbits = cfg["Devices"][device]["stopbits"]
        
        self.modbus_client = ModbusClient(method='RTU',
            port=self.port,
            timeout=5,
            baudrate=self.baudrate,
            parity=self.parity,
            stopbits=self.stopbits,
            bytesize=self.bytesize)

        self.modbus_connected = False
        
        TimerEvtHandle.__init__(self, self.base, interval)
    
    def modbus_connect(self):
        retry_times = 0
        while not self.modbus_connected and retry_times < 5:
            if not self.modbus_client.connect():
                time.sleep(0.5)
                retry_times += 1
                continue
            self.modbus_connected = True
            logging.info('Modbus connected!')

    def timerHandle(self, evt, userdata):
        while 1:
            self.send_fc_data()
            time.sleep(self.interval)

    def send_fc_data(self):
        UNIT = int(cfg["Devices"][self.device]["addr"])
        now = datetime.now()
        now = unicode(now.replace(microsecond = 0))
        n = self.device
        regs = cfg["Devices"][self.device]["regs"]
        # log.info(self.get_modbus_fc(UNIT, regs))
        v = ','.join(self.get_modbus_fc(UNIT, regs))
        r = ','.join(str(cfg["Devices"][self.device]["regs"]))
        server = cfg["Server"]["ip"]
        # call modbus func and get values of regs
        # v = '804.,0A.834M%20804.%2010D.834,669,3488,466,1573,932,55,525,32,34,16,6,190,212,1,1,90,2,30,0,50,-120,5,5,20,352,2,2,352,1,1,0,10,10,44,2,0,5,30,30,1,80,0,100,100,0,0,0,0,0,2178,0,0,269,24,90,1,212'
        payload = {'d': now, 'id': 'ID', 'n': n, 'r': r, 'v': v}
        url = "http://" + str(server) + "/data/setReg.php"

        # log.info(payload)

        # try:
        #     logging.info("--- Send FC data ---")
        #     r = requests.get(url, params=payload)
        #     logging.info("status code: " + str(r.status_code))
        # except requests.exceptions.RequestException as e:  # This is the correct syntax
        #     logging.error(e)
 
    def get_modbus_fc(self, unit, regs):
        self.modbus_connect()

        result = []
        logging.info("--- read input registers: ---")
        count = 1
        for i, (k, v) in enumerate(regs.items()):
            with read_lock:
                addr = int(k) * 10 - 1
                logging.info('Addr: {}'.format(k))
                if v == 'i2':
                    count = 1
                    decoded = self.read_fc_register(addr, count, unit)
                    if decoded != 'error':
                        decoded = decoded.decode_16bit_int()
                        logging.info('Decoded result: {}'.format(decoded))
                    result.append(str(decoded))
                if v == 'i4':
                    count = 2
                    decoded = self.read_fc_register(addr, count, unit)
                    if decoded != 'error':
                        decoded = decoded.decode_16bit_int()
                        logging.info('Decoded result: {}'.format(decoded))
                    result.append(str(decoded))
                if v == 'str':
                    count = 5
                    decoded = self.read_fc_register(addr, count, unit)
                    if decoded != 'error':
                        decoded = decoded.decode_string(count)
                        logging.info('Decoded result: {}'.format(decoded))
                    result.append(str(decoded))
                if v == 'u1':
                    count = 1
                    decoded = self.read_fc_register(addr, count, unit)
                    if decoded != 'error':
                        decoded = decoded.decode_16bit_uint()
                        logging.info('Decoded result: {}'.format(decoded))
                    result.append(str(decoded))
                if v == 'u2':
                    count = 2
                    decoded = self.read_fc_register(addr, count, unit)
                    if decoded != 'error':
                        decoded = decoded.decode_32bit_uint()
                        logging.info('Decoded result: {}'.format(decoded))
                    result.append(str(decoded))

        logging.info("read from holding registers success!!!")
        logging.info("Result array: {}".format(result))
        
        self.modbus_client.close()

        return result

    def read_fc_register(self, addr, count, UNIT):
        rr = self.modbus_client.read_holding_registers(addr, count, unit=UNIT)
        if not rr.isError():
            logging.info('Encoded result: {}'.format(rr.registers))
            decoder = BinaryPayloadDecoder.fromRegisters(rr.registers, Endian.Big, Endian.Big)
            return decoder
        else:
            return 'error'
        