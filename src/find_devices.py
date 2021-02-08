# -*- coding:utf-8 -*-
import time
import serial
import sys
import pymodbus
import logging
import config
from pymodbus.pdu import ModbusRequest
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.transaction import ModbusRtuFramer
from pymodbus.exceptions import ModbusIOException, NotImplementedException
from pymodbus.exceptions import InvalidMessageReceivedException
from pymodbus.constants import Defaults

class FindDevices():
    def __init__(self):
        cfg = config.get_config()
        self.cfg = cfg
        self.modbus_connected = False

    def find_all(self):
        devices = []
        cfg = self.cfg
        port = cfg["Port"]
        for dev in cfg["Dev"]:
            for baudrate in cfg["Dev"][dev]["baudrates"]:
                for parity in cfg["Dev"][dev]["parity"]:
                    for stopbit in cfg["Dev"][dev]["stopbits"]:
                        fc_client = ModbusClient(method = 'rtu',
                            port = port,
                            baudrate = baudrate,
                            timeout = 1,
                            parity = parity,
                            stopbits = stopbit)
                        try:
                            rq = fc_client.read_holding_registers(address=16099, count=1, unit = 1)
                            if isinstance(rq, ModbusIOException):
                                devices.append(str(dev) + ' not found at ' + str(baudrate) + ',' + str(parity) + ',' + str(stopbit))
                            else:
                                devices.append(str(dev) + ' founded at ' + str(baudrate) + ',' + str(parity) + ',' + str(stopbit))
                        except (ModbusIOException) as e:
                            devices.append(str(dev) + ' not found at ' + str(baudrate) + ',' + str(parity) + ',' + str(stopbit))
        return devices