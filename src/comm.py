# -*- coding:utf-8 -*-

# Классы устройств

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
from fc_regs import REGS
import regs

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

    def write_modbus_fc(self, reg, value):
        self.modbus_connect()

        UNIT = self.unit
        v = self.regs[reg]
        address = int(reg) * 10 - 1 # Адрес регистра, например: параметра 16-10 - 1610 * 10 - 1 = 16099

        builder = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Big)

        if v == 'i2':
            count = 2
            logging.info('type: {}'.format(v))
            builder.add_16bit_int(value)
            payload = builder.to_registers()
            payload = builder.build()
            self.modbus_client.write_registers(address, payload, skip_encode=True, unit=UNIT)
        if v == 'i4':
            count = 2
            logging.info('type: {}'.format(v))
            builder.add_32bit_int(value)
            payload = builder.to_registers()
            payload = builder.build()
            self.modbus_client.write_registers(address, payload, skip_encode=True, unit=UNIT)
        if v == 'u1':
            count = 2
            logging.info('type: {}'.format(v))
            builder.add_8bit_uint(value)
            payload = builder.to_registers()
            payload = builder.build()
            self.modbus_client.write_registers(address, payload, skip_encode=True, unit=UNIT)
        if v == 'u2':
            count = 2
            logging.info('type: {}'.format(v))
            builder.add_16bit_uint(value)
            payload = builder.to_registers()
            payload = builder.build()
            self.modbus_client.write_registers(address, payload, skip_encode=True, unit=UNIT)

        return False

    def get_modbus_fc(self):
        self.modbus_connect()

        unit = self.unit
        regs = self.regs

        result = []
        logging.info("--- read input registers: ---")
        count = 1
        # for i, (k, v) in enumerate(regs.items()):
        for k in sorted(regs.keys()):
            v = regs[k]
            with read_lock:
                addr = int(k) * 10 - 1
                logging.info('Addr: {}'.format(k))
                if v == 'i2':
                    count = 2
                    logging.info('type: {}'.format(v))
                    decoded = self.read_fc_register(addr, count, unit)
                    if decoded != 'error':
                        decoded = decoded.decode_16bit_int()
                        logging.info('Decoded result: {}'.format(decoded))
                    result.append(str(decoded))
                if v == 'i4':
                    logging.info('type: {}'.format(v))
                    count = 4
                    decoded = self.read_fc_register(addr, count, unit)
                    if decoded != 'error':
                        decoded = decoded.decode_32bit_int()
                        logging.info('Decoded result: {}'.format(decoded))
                    result.append(str(decoded))
                if v == 's5':
                    logging.info('type: {}'.format(v))
                    count = 5
                    decoded = self.read_fc_register(addr, count, unit)
                    if decoded != 'error':
                        decoded = decoded.decode_string(count)
                        logging.info('Decoded result: {}'.format(decoded))
                    result.append(str(decoded))
                if v == 's20':
                    logging.info('type: {}'.format(v))
                    count = 10
                    decoded = self.read_fc_register(addr, count, unit)
                    if decoded != 'error':
                        decoded = decoded.decode_string(count)
                        logging.info('Decoded result: {}'.format(decoded))
                    result.append(str(decoded))
                if v == 'u1':
                    logging.info('type: {}'.format(v))
                    count = 1
                    decoded = self.read_fc_register(addr, count, unit)
                    if decoded != 'error':
                        decoded = decoded.decode_16bit_uint()
                        logging.info('Decoded result: {}'.format(decoded))
                    result.append(str(decoded))
                if v == 'u2':
                    logging.info('type: {}'.format(v))
                    count = 2
                    decoded = self.read_fc_register(addr, count, unit)
                    if decoded != 'error':
                        decoded = decoded.decode_16bit_uint()
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


class RS485():
    def __init__(self, cfg, device):
        self.unit = int(cfg["Devices"][device]['addr'])
        self.device = device
        self.regs = cfg["Devices"][self.device]["regs"]
        self.addr = 0
        self.cfg = cfg
        self.readTimeout = .1
        self.serial_client = serial.Serial(port=cfg["Port"],
                                          timeout=cfg["Devices"][device]["Timeout"],
                                          baudrate=cfg["Devices"][device]["baudrate"],
                                          parity=serial.PARITY_NONE,
                                          stopbits=serial.STOPBITS_ONE,
                                          bytesize=serial.EIGHTBITS)

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
        # logging.info('send Response:')
        # logging.info(' '.join('{:02x}'.format(x) for x in bytearray(response)))
        
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
                return bytearray(response)
            else:
                return False
        except:
            return False

    def get_access(self, addr=0):
        cmd = [int2byte(addr), int2byte(1), int2byte(1), int2byte(1), int2byte(1), int2byte(1), int2byte(1), int2byte(1), int2byte(1)]
        # print(cmd)
        crc = computeCRC(cmd)
        cmd = cmd + self.long_to_bytes(crc)
        cmd = bytearray(cmd)

        # logging.info("Getting access to Mercury")
        # logging.info(' '.join('{:02x}'.format(x) for x in bytearray(cmd)))

        response = self.send_command(cmd)
        if response:
            # logging.info("Response:")
            # logging.info(' '.join('{:02x}'.format(x) for x in bytearray(response)))
            return True
        
        return False

    def connected(self):
        retry_times = 0
        while not self.access and retry_times < 5:
            # self.addr = self.findMerc()
            if not self.get_access(0):
                time.sleep(0.5)
                retry_times += 1
                continue
            self.access = True
            # logging.info('Mercury access granted')

    # def findMerc(self):
    #     for id in range(200, 205):
    #         cmd = []
    #         cmd.append(int2byte(id))
    #         cmd.append(int2byte(0))
    #         crc = computeCRC(cmd)
    #         cmd = cmd + self.long_to_bytes(crc)
    #         cmd = bytearray(cmd)

    #         logging.info("Searchin for Mercury address")
    #         logging.info("id: {}".format(id))
    #         if self.send_command(cmd, 4) == cmd:
    #             logging.info("Found Mercury")
    #             logging.info("Address: {}".format(id))
    #             return id

    def get_freq(self):
        lenght = 6
        koef = 100
        cmd = [int2byte(0), int2byte(8), int2byte(17), int2byte(64)]
        crc = computeCRC(cmd)
        cmd = cmd + self.long_to_bytes(crc)
        cmd = bytearray(cmd)
        # logging.info("get_Freq cmd:")
        # logging.info(' '.join('{:02x}'.format(x) for x in bytearray(cmd)))

        if self.access:
            response = self.send_command(cmd, lenght)
            # logging.info("get_Freq Response: {}".format(response))
            if response:
                value = response[2]
                value += response[3] << 8
                value += response[1] << 16
                value = float(value)
                # logging.info("get_Freq value: {}".format(value))
                return value / koef
        return False

    def get_current(self, phase):
        lenght = 6
        koef = 1000
        cmd = [int2byte(0), int2byte(8), int2byte(17), int2byte(phase + 32)]
        crc = computeCRC(cmd)
        cmd = cmd + self.long_to_bytes(crc)
        cmd = bytearray(cmd)
        # logging.info("A cmd:")
        # logging.info(' '.join('{:02x}'.format(x) for x in bytearray(cmd)))

        if self.access:
            response = self.send_command(cmd, lenght)
            # logging.info("A{} Response: {}".format(phase, response))
            if response:
                value = 0.000
                value = response[2]
                value += response[3] << 8
                value += response[1] << 16
                value = float(value)
                # logging.info("A value: {}".format(value / koef))
                return value / koef
        return False

    def get_voltage(self, phase):
        lenght = 6
        koef = 100
        cmd = [int2byte(0), int2byte(8), int2byte(17), int2byte(phase + 16)]
        crc = computeCRC(cmd)
        cmd = cmd + self.long_to_bytes(crc)
        cmd = bytearray(cmd)
        # logging.info("V cmd:")
        # logging.info(' '.join('{:02x}'.format(x) for x in bytearray(cmd)))

        if self.access:
            response = self.send_command(cmd, lenght)
            # logging.info("V{} Response: {}".format(phase, response))
            if response:
                value = 0.00
                value = response[2]
                value += response[3] << 8
                value += response[1] << 16
                value = float(value)
                # logging.info("V value: {}".format(value / koef))
                return value / koef
        return False

    # def get_power(self):
    #     # cmd = [0x00, 0x08, 0x16, 0x00]
    #     lenght = 6
    #     koef = 100 * 1000
    #     cmd = [int2byte(0), int2byte(8), int2byte(22), int2byte(0)]
    #     crc = computeCRC(cmd)
    #     cmd = cmd + self.long_to_bytes(crc)
    #     cmd = bytearray(cmd)
    #     logging.info("Power cmd:")
    #     logging.info(' '.join('{:02x}'.format(x) for x in bytearray(cmd)))

    #     if self.access:
    #         response = self.send_command(cmd, lenght)
    #         logging.info("Power Response:")
    #         logging.info(' '.join('{:02x}'.format(x) for x in bytearray(response)))
    #         if response:
    #             value = response[2]
    #             value += response[3] << 8
    #             value += response[1] << 16
    #             value = float(value)
    #             logging.info("Power value: {}".format(value))
    #             return round((value / koef), 2)
    #     return False

    def get_activePower_last_day(self):
        cmd = [0x00, 0x05, 0x00, 0x00]
        lenght = 19
        koef = 1000
        cmd = [int2byte(0), int2byte(5), int2byte(5), int2byte(0)]
        crc = computeCRC(cmd)
        cmd = cmd + self.long_to_bytes(crc)
        cmd = bytearray(cmd)
        # logging.info("Active cmd:")
        # logging.info(' '.join('{:02x}'.format(x) for x in bytearray(cmd)))

        if self.access:
            response = self.send_command(cmd, lenght)
            # logging.info("Active  Response:")
            # logging.info(' '.join('{:02x}'.format(x) for x in bytearray(response)))
            if response:
                value = response[3]
                value += response[4] << 8
                value += response[1] << 16
                value += response[2] << 24
                value = float(value)
                # logging.info("Active  value: {}".format(value))
                return value / koef
        return False

    def get_activePower(self):
        lenght = 19
        koef = 1000
        cmd = [int2byte(0), int2byte(5), int2byte(4), int2byte(0)]
        crc = computeCRC(cmd)
        cmd = cmd + self.long_to_bytes(crc)
        cmd = bytearray(cmd)
        # logging.info("Active cmd:")
        # logging.info(' '.join('{:02x}'.format(x) for x in bytearray(cmd)))

        if self.access:
            response = self.send_command(cmd, lenght)
            # logging.info("Active  Response:")
            # logging.info(' '.join('{:02x}'.format(x) for x in bytearray(response)))
            if response:
                value = response[3]
                value += response[4] << 8
                value += response[1] << 16
                value += response[2] << 24
                value = float(value)
                # logging.info("Active  value: {}".format(value))
                return value / koef
        return False

    def get_sumPower(self):
        # cmd = [0x00, 0x08, 0x11, 0x00]
        lenght = 6
        koef = 100 * 1000
        cmd = [int2byte(0), int2byte(8), int2byte(17), int2byte(0)]
        crc = computeCRC(cmd)
        cmd = cmd + self.long_to_bytes(crc)
        cmd = bytearray(cmd)
        # logging.info("Sum cmd:")
        # logging.info(' '.join('{:02x}'.format(x) for x in bytearray(cmd)))

        if self.access:
            response = self.send_command(cmd, lenght)
            # logging.info("Sum  Response:")
            # logging.info(' '.join('{:02x}'.format(x) for x in bytearray(response)))
            if response:
                value = response[2]
                value += response[3] << 8
                value += response[1] << 16
                value = float(value)
                # logging.info("Active  value: {}".format(value))
                return round((value / koef), 2)
        return False

    def get_data(self):
        self.connected()
        
        freq = '%.2f'%self.get_freq()
        
        temp = '%.2f'%24.00

        a1 = '%.2f'%self.get_current(1)
        a2 = '%.2f'%self.get_current(2)
        a3 = '%.2f'%self.get_current(3)

        v1 = '%.2f'%self.get_voltage(1)
        v2 = '%.2f'%self.get_voltage(2)
        v3 = '%.2f'%self.get_voltage(3)

        last_day = '%.2f'%self.get_activePower_last_day()
        
        today = '%.2f'%self.get_activePower()

        sumPower = '%.2f'%self.get_sumPower()

        # power = '%.2f'%self.get_power()
        # /data/setElectric.php?d=2020-11-05%2016:58:35&id=&n=2&r=1,2,3,4,5,6,7,8,9,10,11&v=
        # 1 - 61061.85,
        # 2 - 61109.58,
        # 3 - 24.00,
        # 4 - 2.05,
        # 5 - 5.95,
        # 6 - 5.32,
        # 7 - 225.11,
        # 8 - 228.99,
        # 9 - 226.07,
        # 10- 49.98,
        # 11- 4592.30
        response = [last_day,today,temp,a1,a2,a3,v1,v2,v3,freq,sumPower]
        # logging.info("response: {}".format(response))
        return response

