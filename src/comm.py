# -*- coding:utf-8 -*-
# import regs
import time
import threading
from datetime import datetime
import logging

# Modbus
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.exceptions import ModbusIOException
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder

# RS 485
import serial
from pymodbus.utilities import computeCRC, checkCRC
from pymodbus.compat import int2byte

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
                    logging.info('type: {}'.format(v))
                    decoded = self.read_fc_register(addr, count, unit)
                    if decoded != 0:
                        decoded = decoded.decode_16bit_int()
                        logging.info('Decoded result: {}'.format(decoded))
                    result.append(str(decoded))
                if v == 'i4':
                    logging.info('type: {}'.format(v))
                    count = 2
                    decoded = self.read_fc_register(addr, count, unit)
                    if decoded != 0:
                        decoded = decoded.decode_16bit_int()
                        logging.info('Decoded result: {}'.format(decoded))
                    result.append(str(decoded))
                if v == 'str':
                    logging.info('type: {}'.format(v))
                    count = 5
                    decoded = self.read_fc_register(addr, count, unit)
                    if decoded != 0:
                        decoded = decoded.decode_string(count)
                        logging.info('Decoded result: {}'.format(decoded))
                    result.append(str(decoded))
                if v == 'u1':
                    logging.info('type: {}'.format(v))
                    count = 1
                    decoded = self.read_fc_register(addr, count, unit)
                    if decoded != 0:
                        decoded = decoded.decode_16bit_uint()
                        logging.info('Decoded result: {}'.format(decoded))
                    result.append(str(decoded))
                if v == 'u2':
                    logging.info('type: {}'.format(v))
                    count = 2
                    decoded = self.read_fc_register(addr, count, unit)
                    if decoded != 0:
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
            # logging.info('Encoded result: {}'.format(rr.registers))
            decoder = BinaryPayloadDecoder.fromRegisters(rr.registers, Endian.Big, Endian.Big)
            return decoder
        else:
            return 0


class RS485():
    def __init__(self, cfg, device):
        
        self.unit = int(cfg["Devices"][device]['addr'])

        self.device = device
        
        self.regs = cfg["Devices"][self.device]["regs"]
        
        self.cfg = cfg
        
        self.readTimeout = .100

        self.serial_client = serial.Serial(port=cfg["Port"],
                                          timeout=cfg["Devices"][device]["Timeout"],
                                          baudrate=cfg["Devices"][device]["baudrate"],
                                          parity=cfg["Devices"][device]["parity"],
                                          stopbits=cfg["Devices"][device]["stopbits"],
                                          bytesize=cfg["Devices"][device]["bytesize"])

        self.access = False


    def long_to_bytes(self, i):
        byte_array = []
        while i != 0:
            byte_array = [int2byte(i % 256)] + byte_array
            i = i // 256
        return byte_array

    def send_command(self, cmd, lenght = 4):
        
        self.serial_client.write(cmd)
        time.sleep(self.readTimeout)

        response = self.serial_client.read(lenght)

        try:
            crc = []
            crc.append(response[lenght-2])
            crc.append(response[lenght-1])
            # print(crc)
            crc_val = (ord(crc[0]) << 8) + ord(crc[1])
            # print(crc_val)
            data = response[:lenght - 2]
            # print(hex(pymodbus.utilities.computeCRC(data)))
            if checkCRC(data, crc_val):
                return response
            else:
                return False
        except:
            return False

    def get_access(self, addr):
        cmd = [addr, int2byte(1), int2byte(1), int2byte(1), int2byte(1), int2byte(1), int2byte(1), int2byte(1), int2byte(1)]
        # print(cmd)
        crc = computeCRC(cmd)
        cmd = cmd + self.long_to_bytes(crc)
        cmd = bytearray(cmd)

        # print('Command: ' + cmd)
        response = self.send_command(cmd)
        if response:
            return True
        
        return False
        # print ('Response: ' + bytearray(response))

    def connected(self):
        retry_times = 0
        while not self.access and retry_times < 5:
            if not self.get_access():
                time.sleep(0.5)
                retry_times += 1
                continue
            self.access = True
            logging.info('Mercury access grant')

    def findMerc(self):
        for id in range(200, 205):
            cmd = []
            cmd.append(int2byte(id))
            cmd.append(int2byte(0))
            crc = computeCRC(cmd)
            cmd = cmd + self.long_to_bytes(crc)
            cmd = bytearray(cmd)
            print(cmd)
            if self.send_command(cmd, 4) == cmd:
                print('Found')
                return id

    def get_data(self):
        addr = self.findMerc()
        self.get_access(addr)