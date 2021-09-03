class AbstractReg:
    LENGTH = 0

    def __init__(self, reg_id=None, reg_addr=None, raw: bytes = None, value=None):
        self._id = None
        self._addr = None
        self._raw = None
        self._value = None

        if reg_id is not None:
            self.id = reg_id
        elif reg_addr is not None:
            self.addr = reg_addr

        if raw is not None:
            self.raw = raw
        elif value is not None:
            self.value = value

    def _calc_value_by_raw(self):
        raise NotImplementedError

    def _calc_raw_by_value(self):
        raise NotImplementedError

    def _set_addr_by_id(self):
        self._addr = self._id

    def _set_id_by_addr(self):
        self._id = self._addr

    def __setattr__(self, key, value):
        if key == 'id':
            self._id = value
            self._set_addr_by_id()
        elif key == 'addr':
            self._addr = value
            self._set_id_by_addr()
        elif key == 'raw':
            self._raw = value
            self._calc_value_by_raw()
        elif key == 'value':
            self._value = value
            self._calc_raw_by_value()
        else:
            super().__setattr__(key, value)

    def __getattr__(self, item):
        if item == 'id':
            return self._id
        elif item == 'addr':
            return self._addr
        elif item == 'raw':
            return self._raw
        elif item == 'value':
            return self._value
        else:
            super().__getattribute__(item)


class GenericWriteResultReg(AbstractReg):
    LENGTH = 1

    def _calc_value_by_raw(self):
        length = len(self._raw)
        val = int(self._raw[length - self.LENGTH:].hex(), 16)
        self._value = 'OK' if val == 0 else 'ERROR'

    def _calc_raw_by_value(self):
        tmp = []
        if self._value == 'OK':
            val = 0
        else:
            val = 1
        for i in range(self.LENGTH - 1, -1, -1):
            tmp.append((val >> (i * 8)) & 0xFF)
        self._raw = bytes(tmp)

    def __str__(self):
        pattern = '%s:%s'
        return pattern % (str(self.id), self.value)

    def __repr__(self):
        return str(self)


class GenericUintReg(AbstractReg):
    def _calc_value_by_raw(self):
        if self.LENGTH == 0:
            raise NotImplementedError('Length not set')
        length = len(self._raw)
        self._value = int(self._raw[length - self.LENGTH:].hex(), 16)

    def _calc_raw_by_value(self):
        tmp = []
        for i in range(self.LENGTH - 1, -1, -1):
            tmp.append((self._value >> (i * 8)) & 0xFF)
        self._raw = bytes(tmp)

    def __str__(self):
        pattern = '%s:0x%.' + str(self.LENGTH * 2) + 'X'
        return pattern % (str(self.id), self.value)

    def __repr__(self):
        return str(self)


class GenericUint8Reg(GenericUintReg):
    LENGTH = 1


class GenericInt8Reg(GenericUint8Reg):
    def _calc_value_by_raw(self):
        super()._calc_value_by_raw()
        if self._value & 0x80:
            self._value &= 0x7F
            self._value = -(self._value ^ 0x7F)

    def _calc_raw_by_value(self):
        if self._value < 0:
            self._raw = bytes([(-self._value ^ 0xFF) & 0xFF])
        else:
            self._raw = bytes([self._value & 0xFF])

    def __str__(self):
        pattern = '%s:%d'
        return pattern % (str(self.id), self.value)

    def __repr__(self):
        return str(self)


class GenericUint16Reg(GenericUintReg):
    LENGTH = 2


class GenericInt16Reg(GenericUint16Reg):
    def _calc_value_by_raw(self):
        super()._calc_value_by_raw()
        if self._value & 0x8000:
            self._value &= 0x7FFF
            self._value = -(self._value ^ 0x7FFF)

    def _calc_raw_by_value(self):
        tmp = []
        if self._value < 0:
            val = (-self._value ^ 0xFFFF) & 0xFFFF
        else:
            val = self._value & 0xFFFF
        for i in range(1, -1, -1):
            tmp.append((val >> (i * 8)) & 0xFF)

        self._raw = bytes(tmp)

    def __str__(self):
        pattern = '%s:%d'
        return pattern % (str(self.id), self.value)

    def __repr__(self):
        return str(self)


class GenericUint32Reg(GenericUintReg):
    LENGTH = 4


class GenericInt32Reg(GenericUint32Reg):
    def _calc_value_by_raw(self):
        super()._calc_value_by_raw()
        if self._value & 0x80000000:
            self._value &= 0x7FFFFFFF
            self._value = -(self._value ^ 0x7FFFFFFF)

    def _calc_raw_by_value(self):
        tmp = []
        if self._value < 0:
            val = (-self._value ^ 0xFFFFFFFF) & 0xFFFFFFFF
        else:
            val = self._value & 0xFFFFFFFF
        for i in range(3, -1, -1):
            tmp.append((val >> (i * 8)) & 0xFF)

        self._raw = bytes(tmp)

    def __str__(self):
        pattern = '%s:%d'
        return pattern % (str(self.id), self.value)

    def __repr__(self):
        return str(self)


class GenericFractionReg(AbstractReg):
    PRECISION = 0

    def _calc_value_by_raw(self):
        if self.LENGTH == 0:
            raise NotImplementedError('Length not set')
        length = len(self._raw)
        self._value = int(self._raw[length - self.LENGTH:].hex(), 16) / float(
            10 ** self.PRECISION)

    def _calc_raw_by_value(self):
        tmp = []
        val = int(self._value * (10 ** self.PRECISION))
        for i in range(self.LENGTH - 1, -1, -1):
            tmp.append((val >> (i * 8)) & 0xFF)
        self._raw = bytes(tmp)

    def __str__(self):
        pattern = '%s:%.' + str(self.PRECISION) + 'f'
        return pattern % (str(self.id), self.value)

    def __repr__(self):
        return str(self)


class GenericFraction32Reg(GenericFractionReg):
    LENGTH = 4


class GenericFraction16Reg(GenericFractionReg):
    LENGTH = 2


class GenericFraction8Reg(GenericFractionReg):
    LENGTH = 1


class DanfossUint32Reg(GenericUint32Reg):
    def _set_addr_by_id(self):
        self._addr = (self._id * 10) - 1

    def _set_id_by_addr(self):
        self._id = int((self._addr + 1) / 10)


class DanfossInt32Reg(GenericInt32Reg):
    def _set_addr_by_id(self):
        self._addr = (self._id * 10) - 1

    def _set_id_by_addr(self):
        self._id = int((self._addr + 1) / 10)


class DanfossUint16Reg(GenericUint16Reg):
    def _set_addr_by_id(self):
        self._addr = (self._id * 10) - 1

    def _set_id_by_addr(self):
        self._id = int((self._addr + 1) / 10)


class DanfossInt16Reg(GenericInt16Reg):
    def _set_addr_by_id(self):
        self._addr = (self._id * 10) - 1

    def _set_id_by_addr(self):
        self._id = int((self._addr + 1) / 10)


class DanfossUint16RegIn32Reg(DanfossUint32Reg):
    def _calc_value_by_raw(self):
        if self.LENGTH == 0:
            raise NotImplementedError('Length not set')
        length = len(self._raw)
        self._value = int(self._raw[length - self.LENGTH:-2].hex(), 16)


class DanfossWriteResultReg(GenericWriteResultReg):
    def _set_addr_by_id(self):
        self._addr = (self._id * 10) - 1

    def _set_id_by_addr(self):
        self._id = int((self._addr + 1) / 10)


class MercuryReg(AbstractReg):
    LENGTH = 0
    PRECISION = 0

    def _get_uint(self):
        raise NotImplementedError

    def _get_raw(self, val: int):
        raise NotImplementedError

    def _calc_value_by_raw(self):
        self._value = self._get_uint() / float(10 ** self.PRECISION)

    def _calc_raw_by_value(self):
        self._raw = self._get_raw(int(self._value * (10 ** self.PRECISION)))

    def __str__(self):
        pattern = '%s:%.' + str(self.PRECISION) + 'f'
        return pattern % (str(self.id), self.value)

    def __repr__(self):
        return str(self)


class MercuryUint32Reg(MercuryReg):
    LENGTH = 4

    def _get_uint(self):
        val = self._raw[2]
        val += self._raw[3] << 8
        val += self._raw[0] << 16
        val += self._raw[1] << 24

        return val

    def _get_raw(self, val: int):
        tmp = list()
        tmp.append((val >> 16) & 0xFF)
        tmp.append((val >> 24) & 0xFF)
        tmp.append(val & 0xFF)
        tmp.append((val >> 8) & 0xFF)

        return bytes(tmp)


class MercuryUint24Reg(MercuryReg):
    LENGTH = 3

    def _get_uint(self):
        val = self._raw[1]
        val += self._raw[2] << 8
        val += self._raw[0] << 16

        return val

    def _get_raw(self, val: int):
        tmp = list()
        tmp.append((val >> 16) & 0xFF)
        tmp.append(val & 0xFF)
        tmp.append((val >> 8) & 0xFF)

        return bytes(tmp)


class MercuryCounterReg(MercuryUint32Reg):
    PRECISION = 3


class MercuryVoltageReg(MercuryUint24Reg):
    PRECISION = 2


class MercuryCurrentReg(MercuryUint24Reg):
    PRECISION = 3


class MercuryFreqReg(MercuryUint24Reg):
    PRECISION = 2


class MercuryActPowerReg(MercuryUint24Reg):
    PRECISION = 2

    def _get_uint(self):
        val = super()._get_uint()
        result = val & 0x3FFFFF
        sign = val & 0x800000
        if sign:
            result *= -1

        return result


class NevaEnergyReg(GenericFraction32Reg):
    PRECISION = 2


class NevaPowerReg(GenericFraction32Reg):
    PRECISION = 2


class NevaCurrentReg(GenericFraction16Reg):
    PRECISION = 3


class NevaVoltageReg(GenericFraction16Reg):
    PRECISION = 2


class NevaFreqReg(GenericFraction16Reg):
    PRECISION = 2


class NevaTemperatureReg(GenericInt8Reg):
    PRECISION = 0
