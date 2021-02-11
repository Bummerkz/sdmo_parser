# -*- coding:utf-8 -*-
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder

import time
import threading
from datetime import datetime
import logging
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.exceptions import ModbusIOException

read_lock = threading.Lock()

class Modbus():
    def __init__(self, cfg, device):
        
        self.unit = int(cfg["Devices"][device]['addr'])

        self.device = device
        
        self.regs = cfg["Devices"][self.device]["regs"]
        
        self.cfg = cfg

        self.modbus_client = ModbusClient(method='RTU',
                                          port=cfg["Port"],
                                          timeout=cfg["Devices"][device]["Timeout"],
                                          baudrate=cfg["Devices"][device]["baudrate"],
                                          parity=cfg["Devices"][device]["parity"],
                                          stopbits=cfg["Devices"][device]["stopbits"],
                                          bytesize=cfg["Devices"][device]["bytesize"])

        self.modbus_connected = False

    def modbus_connect(self):
        retry_times = 0
        while not self.modbus_connected and retry_times < 5:
            if not self.modbus_client.connect():
                time.sleep(0.5)
                retry_times += 1
                continue
            self.modbus_connected = True
            logging.info('Modbus connected!')

    def get_modbus_fc(self):
        self.modbus_connect()

        unit = self.unit
        regs = self.regs

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