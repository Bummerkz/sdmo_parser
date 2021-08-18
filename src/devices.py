import regs


class AbstractDevice:
    DEVICE_ID = 0xFF
    REGS = []
    SETTINGS = []
    API_ID = None

    def process(self, data: bytes):
        raise NotImplementedError

    def get_register(self, reg_id, reg_value):
        if len(self.SETTINGS) == 0:
            raise NoSettingsException


class MultiPacketDevice(AbstractDevice):
    def process(self, data: bytes):
        return self._parse(data, self.REGS)

    def process_settings(self, data: bytes):
        return self._parse(data, self.SETTINGS)

    @staticmethod
    def _parse(data: bytes, subject: list):
        result = []
        packet_number = data[0] >> 4
        # packets_total = data[0] & 0xF
        pos = 1
        for reg in subject:
            if reg.get('packet_number') in (None, packet_number):
                register = reg['class']()
                register.id = reg['id']
                register.raw = data[pos:pos + reg['class'].LENGTH]
                result.append(register)
                pos += reg['class'].LENGTH
        return result


class SinglePacketDevice(AbstractDevice):
    def process(self, data: bytes):
        result = []
        pos = 0
        for reg in self.REGS:
            register = reg['class']()
            register.id = reg['id']
            register.raw = data[pos:pos + reg['class'].LENGTH]
            result.append(register)
            pos += reg['class'].LENGTH
        return result


class DanfossDevice(MultiPacketDevice):
    DEVICE_ID = 0xF4
    API_ID = 1

    REGS = [
        {
            'id': 1630,  # 0x3FAB,
            'class': regs.DanfossUint16Reg,
            'lenght': 1,
        },
        {
            'id': 1610,  # 0x3EE3,
            'class': regs.DanfossInt32Reg,
            'packet_number': 1,
        },
        {
            'id': 1612,  # 0x3EF7,
            'class': regs.DanfossUint16Reg,
            'packet_number': 1,
        },
        {
            'id': 1613,  # 0x3F01,
            'class': regs.DanfossUint16Reg,
            'packet_number': 1,
        },
        {
            'id': 1614,  # 0x3F0B,
            'class': regs.DanfossInt32Reg,
            'packet_number': 1,
        },
        {
            'id': 1617,  # 0x3F29,
            'class': regs.DanfossInt32Reg,
            'packet_number': 1,
        },
        {
            'id': 1622,  # 0x3F5B,
            'class': regs.DanfossInt16Reg,
            'packet_number': 1,
        },
        {
            'id': 1634,  # 0x3FD3,
            'class': regs.DanfossUint16Reg,
            'packet_number': 1,
        },
        {
            'id': 1639,  # 0x4005,
            'class': regs.DanfossUint16Reg,
            'packet_number': 1,
        },
        {
            'id': 1660,  # 0x40D7,
            'class': regs.DanfossUint16Reg,
            'packet_number': 1,
        },
        {
            'id': 1998,  # 0x4E0B,
            'class': regs.DanfossUint32Reg,
            'packet_number': 1,
        },
        {
            'id': 1951,  # 0x4C35,
            'class': regs.DanfossUint32Reg,
            'packet_number': 1,
        },
        {
            'id': 1956,  # 0x4C67,
            'class': regs.DanfossUint32Reg,
            'packet_number': 1,
        },
        {
            'id': 1957,  # 0x4C71,
            'class': regs.DanfossUint32Reg,
            'packet_number': 1,
        },
        {
            'id': 1959,  # 0x4C85,
            'class': regs.DanfossUint32Reg,
            'packet_number': 1,
        },
        {
            'id': 1997,  # 0x4E01,
            'class': regs.DanfossUint32Reg,
            'packet_number': 2,
        },
        {
            'id': 1999,  # 0x4E15,
            'class': regs.DanfossUint32Reg,
            'packet_number': 2,
        }
    ]

    SETTINGS = [
        {
            'id': 1900,  # 0x4A37,
            'class': regs.DanfossUint32Reg,
            'packet_number': 1,
        },
        {
            'id': 1901,  # 0x4A41,
            'class': regs.DanfossUint32Reg,
            'packet_number': 1,
        },
        {
            'id': 1902,  # 0x4A4B,
            'class': regs.DanfossUint32Reg,
            'packet_number': 1,
        },
        {
            'id': 1903,  # 0x4A55,
            'class': regs.DanfossUint32Reg,
            'packet_number': 1,
        },
        {
            'id': 1904,  # 0x4A5F,
            'class': regs.DanfossUint32Reg,
            'packet_number': 1,
        },
        {
            'id': 1908,  # 0x4A87,
            'class': regs.DanfossUint32Reg,
            'packet_number': 1,
        },
        {
            'id': 1909,  # 0x4A91,
            'class': regs.DanfossUint32Reg,
            'packet_number': 1,
        },
        {
            'id': 1910,  # 0x4A9B,
            'class': regs.DanfossUint32Reg,
            'packet_number': 1,
        },
        {
            'id': 1912,  # 0x4AAF,
            'class': regs.DanfossUint32Reg,
            'packet_number': 1,
        },
        {
            'id': 1915,  # 0x4ACD,
            'class': regs.DanfossUint32Reg,
            'packet_number': 1,
        },
        {
            'id': 1917,  # 0x4AE1,
            'class': regs.DanfossInt32Reg,
            'packet_number': 1,
        },
        {
            'id': 1918,  # 0x4AEB,
            'class': regs.DanfossUint32Reg,
            'packet_number': 1,
        },
        {
            'id': 1922,  # 0x4B13,
            'class': regs.DanfossUint32Reg,
            'packet_number': 2,
        },
        {
            'id': 1923,  # 0x4B1D,
            'class': regs.DanfossUint32Reg,
            'packet_number': 2,
        },
        {
            'id': 1924,  # 0x4B27,
            'class': regs.DanfossUint32Reg,
            'packet_number': 2,
        },
        {
            'id': 1925,  # 0x4B31,
            'class': regs.DanfossUint32Reg,
            'packet_number': 2,
        },
        {
            'id': 1926,  # 0x4B3B,
            'class': regs.DanfossUint32Reg,
            'packet_number': 2,
        },
        {
            'id': 1927,  # 0x4B45,
            'class': regs.DanfossUint32Reg,
            'packet_number': 2,
        },
        {
            'id': 1928,  # 0x4B4F,
            'class': regs.DanfossInt32Reg,
            'packet_number': 2,
        },
        {
            'id': 1931,  # 0x4B6D,
            'class': regs.DanfossUint32Reg,
            'packet_number': 2,
        },
        # {
        #     'id': 1945,  # 0x4BF9,
        #     'class': regs.DanfossUint32Reg,
        #     'packet_number': 1,
        # },
        {
            'id': 1946,  # 0x4C03,
            'class': regs.DanfossUint32Reg,
            'packet_number': 2,
        },
        {
            'id': 1947,  # 0x4C0D,
            'class': regs.DanfossUint32Reg,
            'packet_number': 2,
        },
        {
            'id': 1969,  # 0x4CE9
            'class': regs.DanfossUint32Reg,
            'packet_number': 0,
        },
        {
            'id': 1971,  # 0x4CFD
            'class': regs.DanfossUint32Reg,
            'packet_number': 0,
        }
    ]

    def get_register(self, reg_id, reg_value=None):
        for reg in self.SETTINGS:
            if reg['id'] == reg_id:
                register = reg['class']()
                register.id = reg_id
                if reg_value is not None:
                    register.value = reg_value
                return register
        raise UnknownSettingException

    def get_result_reg(self, reg_addr, reg_raw=None):
        result = regs.DanfossWriteResultReg()
        result.addr = reg_addr
        if reg_raw is not None:
            result.raw = reg_raw
        return result


class MercuryDevice(SinglePacketDevice):
    DEVICE_ID = 0xE4
    API_ID = 2
    REGS = [
        {
            'id': 1,
            'class': regs.MercuryCounterReg,
        },
        {
            'id': 2,
            'class': regs.MercuryCounterReg,
        },
        {
            'id': 4,
            'class': regs.MercuryCurrentReg,
        },
        {
            'id': 5,
            'class': regs.MercuryCurrentReg,
        },
        {
            'id': 6,
            'class': regs.MercuryCurrentReg,
        },
        {
            'id': 7,
            'class': regs.MercuryVoltageReg,
        },
        {
            'id': 8,
            'class': regs.MercuryVoltageReg,
        },
        {
            'id': 9,
            'class': regs.MercuryVoltageReg,
        },
        {
            'id': 10,
            'class': regs.MercuryFreqReg,
        },
        {
            'id': 11,
            'class': regs.MercuryActPowerReg,
        }
    ]


class NevaDevice(SinglePacketDevice):
    DEVICE_ID = 0xE3
    API_ID = 2
    REGS = [
        {
            'id': 1,
            'class': regs.NevaEnergyReg,
        },
        {
            'id': 2,
            'class': regs.NevaEnergyReg,
        },
        {
            'id': 11,
            'class': regs.NevaPowerReg,
        },
        {
            'id': 4,
            'class': regs.NevaCurrentReg,
        },
        {
            'id': 5,
            'class': regs.NevaCurrentReg,
        },
        {
            'id': 6,
            'class': regs.NevaCurrentReg,
        },
        {
            'id': 7,
            'class': regs.NevaVoltageReg,
        },
        {
            'id': 8,
            'class': regs.NevaVoltageReg,
        },
        {
            'id': 9,
            'class': regs.NevaVoltageReg,
        },
        {
            'id': 10,
            'class': regs.NevaFreqReg,
        },
        {
            'id': 3,
            'class': regs.NevaTemperatureReg,
        }
    ]


class DeviceException(Exception):
    pass


class DeviceNotWritableException(DeviceException):
    pass


class UnknownSettingException(DeviceException):
    pass


class NoSettingsException(DeviceException):
    pass
